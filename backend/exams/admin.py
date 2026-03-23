from django.contrib import admin
from .models import Exam, Question, ExamAttempt, Answer

admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(ExamAttempt)
admin.site.register(Answer)