from django.urls import path
from .views import LogViolationView, ScreenshotUploadView

urlpatterns = [

    path("log/", LogViolationView.as_view(), name="log_violation"),
    path("screenshot/", ScreenshotUploadView.as_view()),

]