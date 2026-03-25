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
            "correct_answer"
        ]


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ['created_by']


    def create(self, validated_data):
        questions_data = validated_data.pop('questions')

        exam = Exam.objects.create(**validated_data)

        for q in questions_data:
            Question.objects.create(
                exam=exam,
                text=q.get('text'),
                option_a=q.get('option_a'),
                option_b=q.get('option_b'),
                option_c=q.get('option_c'),
                option_d=q.get('option_d'),
                correct_answer=q.get('correct_answer')
            )

        return exam


class ExamDetailSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "description",
            "duration",
            "questions",
            "start_time",
            "end_time",
            "is_active",
            "is_published",
        ]