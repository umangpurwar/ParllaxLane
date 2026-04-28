from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Question, Answer, ExamAttempt, Exam
from django.utils.timezone import now
from core.permissions import IsOrgMember, IsOrgAdmin
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit




from .serializers import ExamSerializer, ExamDetailSerializer
from monitoring.models import Violation


class ExamListView(generics.ListAPIView):

    serializer_class = ExamSerializer
    permission_classes = [IsOrgMember]

    def get_queryset(self):
        org = self.request.user.current_organisation
        return Exam.objects.filter(
            organisation=org,
            is_published=True
        )


class ExamDetailView(generics.RetrieveAPIView):

    serializer_class = ExamDetailSerializer
    permission_classes = [IsOrgMember]

    def get_queryset(self):
        org = self.request.user.current_organisation
        return Exam.objects.filter(
            organisation=org,
            is_published=True
        )

class StartExamView(generics.GenericAPIView):

    permission_classes = [IsOrgMember]

    @method_decorator(ratelimit(key='user', rate='5/m', method='POST', block=True))
    def post(self, request, pk):

        org = request.user.current_organisation

        try:
            exam = Exam.objects.get(pk=pk, organisation=org)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=404)

        if not exam.is_active:
            return Response({"error": "Exam is disabled"}, status=403)

        attempt = ExamAttempt.objects.create(
            user=request.user,
            exam=exam
        )

        return Response({
            "attempt_id": attempt.id,
            "exam_id": exam.id
        })

class SubmitExamView(generics.GenericAPIView):
    permission_classes = [IsOrgMember]

    @method_decorator(ratelimit(key='user', rate='3/m', method='POST', block=True))
    def post(self, request, pk):

        user = request.user
        org = user.current_organisation

        try:
            exam = Exam.objects.get(pk=pk, organisation=org)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=404)

        if not exam.is_active:
            return Response({"error": "Exam is disabled"}, status=403)

        attempt = ExamAttempt.objects.filter(
            user=user,
            exam=exam
        ).last()

        if not attempt:
            return Response({"error": "No active exam attempt found"}, status=400)

        if attempt.status == "terminated":
            return Response({"error": "Exam has been terminated"}, status=403)

        answers = request.data.get("answers", {})
        score = 0

        for question_id, selected in answers.items():
            try:
                question = Question.objects.get(
                    id=question_id,
                    exam=exam   
                )
                Answer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=selected
                )
                if selected == question.correct_answer:
                    score += 1
            except Question.DoesNotExist:
                continue

        attempt.score = score
        attempt.status = "completed"
        attempt.end_time = now()
        attempt.save()

        return Response({
            "score": score,
            "total": exam.questions.count()
        })

@api_view(['GET'])
@permission_classes([IsOrgMember])
def my_results(request):

    org = request.user.current_organisation

    attempts = ExamAttempt.objects.filter(
        user=request.user,
        exam__organisation=org, 
        status__in=['completed', 'terminated']
    ).select_related('exam')

    data = []
    for attempt in attempts:
        total_questions = attempt.exam.questions.count()

        data.append({
            "id": attempt.id,
            "exam_title": attempt.exam.title,
            "score": attempt.score or 0,
            "total_questions": total_questions,
            "violations": attempt.total_violations,
            "status": attempt.status.capitalize(),
            "date": attempt.start_time
        })

    return Response(data)


class CreateExamView(generics.CreateAPIView):

    serializer_class = ExamSerializer
    permission_classes = [IsOrgAdmin]

    @method_decorator(ratelimit(key='user', rate='2/m', method='POST', block=True))
    def perform_create(self, serializer):

        serializer.save(
            created_by=self.request.user,
            organisation=self.request.user.current_organisation 
        )