from django.db import models
from django.conf import settings
from django.utils.timezone import now

User = settings.AUTH_USER_MODEL


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    is_published = models.BooleanField(default=True)

    is_active = models.BooleanField(default=False)
    violation_limit = models.IntegerField(default=5)
    auto_submit_on_violation = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)

    correct_answer = models.CharField(max_length=1)

    def __str__(self):
        return self.text


class ExamAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    score = models.IntegerField(default=0)
    risk_score = models.IntegerField(default=0)

    status = models.CharField(max_length=20, default="active")
    total_violations = models.IntegerField(default=0)
    last_active = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user} - {self.exam}"


class Answer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.attempt} - {self.question}"