from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction

from .models import Exam, Question, ExamAttempt
from organisations.plan_features import get_plan_features


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "question_type",   
            "image",           
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "points",          
            "order"            
        ]


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = '__all__'
        read_only_fields = ['created_by']

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        org = user.current_organisation

        if not org:
            raise ValidationError("No active organisation selected")

        features = get_plan_features(org)

        questions_data = validated_data.pop('questions')

        #  STEP 4 — limit number of questions
        if len(questions_data) > features["max_questions"]:
            raise ValidationError(
                f"{org.plan} plan allows only {features['max_questions']} questions per exam"
            )

        # VALIDATE ALL QUESTIONS FIRST
        for q in questions_data:

            question_type = q.get("question_type", "mcq")

            # STEP 3 — restrict question types
            if question_type not in features["allowed_question_types"]:
                raise ValidationError(
                    f"{org.plan} plan does not allow '{question_type}' questions"
                )

            # STEP 5 — image restriction
            if q.get("image") and not features["image_questions"]:
                raise ValidationError("Upgrade plan to use image questions")

            # future-proof: file upload restriction
            if question_type == "file_upload" and not features["file_upload"]:
                raise ValidationError("Upgrade plan to use file upload questions")

        # ATOMIC TRANSACTION (VERY IMPORTANT)
        with transaction.atomic():

            exam = Exam.objects.create(
                **validated_data,
                created_by=user
            )

            for q in questions_data:
                Question.objects.create(
                    exam=exam,
                    text=q.get('text'),
                    question_type=q.get("question_type", "mcq"),
                    image=q.get("image"),
                    option_a=q.get('option_a'),
                    option_b=q.get('option_b'),
                    option_c=q.get('option_c'),
                    option_d=q.get('option_d'),
                    correct_answer=q.get('correct_answer'),
                    points=q.get("points", 1),
                    order=q.get("order", 0),
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