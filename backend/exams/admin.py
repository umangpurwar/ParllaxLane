from django.contrib import admin
from .models import Exam, Question, ExamAttempt

admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(ExamAttempt)