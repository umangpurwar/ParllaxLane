from rest_framework import generics
from .models import User
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenSerializer
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    @method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomLoginView(TokenObtainPairView):

    serializer_class = CustomTokenSerializer

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


def health_check(request):
    return JsonResponse({"status": "ok"})