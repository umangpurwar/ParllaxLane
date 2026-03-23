from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import Question, Answer, ExamAttempt, Exam



from .serializers import ExamSerializer, ExamDetailSerializer
from monitoring.models import Violation


class ExamListView(generics.ListAPIView):

    queryset = Exam.objects.filter(is_published=True)
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


class ExamDetailView(generics.RetrieveAPIView):

    queryset = Exam.objects.filter(is_published=True)
    serializer_class = ExamDetailSerializer
    permission_classes = [IsAuthenticated]


class StartExamView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        exam = Exam.objects.get(pk=pk)
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
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            exam = Exam.objects.get(pk=pk)

        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=404)
        if not exam.is_active:
            return Response({"error": "Exam is disabled"}, status=403)

        attempt = ExamAttempt.objects.filter(
            user=user,
            exam=exam
        ).last()

        
        if not attempt:
            return Response({"error": "No active exam attempt found. Did you start the exam?"}, status=400)
        
        if attempt.status == "terminated":
            return Response({"error": "Exam has been terminated"}, status=403)

        answers = request.data.get("answers", {})
        score = 0

        for question_id, selected in answers.items():
            try:
                question = Question.objects.get(id=question_id)
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
        attempt.save()

        return Response({
            "score": score,
            "total": exam.questions.count()
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_results(request):
    attempts = ExamAttempt.objects.filter(
        user=request.user,
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