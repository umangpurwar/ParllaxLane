from django.urls import path
from .views import ExamListView, ExamDetailView, StartExamView, SubmitExamView

urlpatterns = [
    path("", ExamListView.as_view()),
    path("<int:pk>/", ExamDetailView.as_view()),
    path("<int:pk>/start/", StartExamView.as_view()),
    path("<int:pk>/submit/", SubmitExamView.as_view()),
]