from rest_framework import serializers
from .models import Exam, Question, QuestionOption, ExamAttempt, Answer


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "question_type",
            "points",
            "negative_points",
            "order",
            "image",
            "options",
            "correct_text_answer",
            "explanation",
        ]

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])
        question = Question.objects.create(**validated_data)

        for option_data in options_data:
            QuestionOption.objects.create(question=question, **option_data)

        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop("options", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if options_data is not None:
            instance.options.all().delete()
            for option_data in options_data:
                QuestionOption.objects.create(question=instance, **option_data)

        return instance


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "description",
            "start_time",
            "end_time",
            "duration",
            "created_by",
            "organisation",
            "is_published",
            "is_active",
            "violation_limit",
            "auto_submit_on_violation",
            "created_at",
            "questions",
        ]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")
        exam = Exam.objects.create(**validated_data)

        for question_data in questions_data:
            options_data = question_data.pop("options", [])

            question = Question.objects.create(
                exam=exam,
                **question_data
            )

            for option_data in options_data:
                QuestionOption.objects.create(
                    question=question,
                    **option_data
                )

        return exam

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if questions_data is not None:
            instance.questions.all().delete()

            for question_data in questions_data:
                options_data = question_data.pop("options", [])

                question = Question.objects.create(
                    exam=instance,
                    **question_data
                )

                for option_data in options_data:
                    QuestionOption.objects.create(
                        question=question,
                        **option_data
                    )

        return instance


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            "id",
            "attempt",
            "question",
            "selected_option",
            "text_answer",
            "file_upload",
            "is_correct",
        ]


class ExamAttemptSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = ExamAttempt
        fields = [
            "id",
            "user",
            "exam",
            "start_time",
            "end_time",
            "points_scored",
            "total_points",
            "risk_score",
            "total_violations",
            "status",
            "last_active",
            "answers",
        ]