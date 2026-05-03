from django.db import models
from exams.models import ExamAttempt


class Violation(models.Model):
    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name="violations",
        db_index=True
    )

    violation_type = models.CharField(max_length=100)
    severity = models.IntegerField(default=1)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.violation_type} - {self.timestamp}"


class Screenshot(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, db_index=True)

    image = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    flagged = models.BooleanField(default=False)