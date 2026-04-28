from django.urls import path
from .views import RegisterView, health_check

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("health/", health_check),
]