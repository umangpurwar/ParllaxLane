from django.urls import path
from .views import *

urlpatterns = [
    path("", ExamListView.as_view()),
    path('exam/create/', CreateExamView.as_view()),
    path("my-results/", my_results),
    path("<int:pk>/", ExamDetailView.as_view()),
    path("<int:pk>/start/", StartExamView.as_view()),
    path("<int:pk>/submit/", SubmitExamView.as_view()),
]