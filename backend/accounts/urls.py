from django.urls import path
from .views import RegisterView, SendOTPView, VerifyOTPView, GoogleAuthView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("send-otp/", SendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("google/", GoogleAuthView.as_view()),

]