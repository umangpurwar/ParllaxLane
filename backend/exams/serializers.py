from rest_framework import serializers
from .models import Exam, Question, ExamAttempt


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
        ]


class ExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "description",
            "duration",
        ]


class ExamDetailSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "description",
            "duration",
            "questions",
        ]