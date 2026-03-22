from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Question, Answer

from .models import Exam, ExamAttempt
from .serializers import ExamSerializer, ExamDetailSerializer


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

        exam = Exam.objects.get(pk=pk)

        attempt = ExamAttempt.objects.filter(
            user=user,
            exam=exam
        ).last()

        answers = request.data.get("answers", {})

        score = 0

        for question_id, selected in answers.items():

            question = Question.objects.get(id=question_id)

            Answer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected
            )

            if selected == question.correct_answer:
                score += 1

        attempt.score = score
        attempt.save()

        return Response({
            "score": score,
            "total": exam.questions.count()
        })