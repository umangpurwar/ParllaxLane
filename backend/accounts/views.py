from rest_framework import generics
from .models import User, EmailOTP
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenSerializer
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils.timezone import now
import random
from django.contrib.auth import get_user_model
import requests
from rest_framework import status

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

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


class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email required"}, status=400)

        email = email.lower().strip()

        # CHECK USER EXISTS
        if not User.objects.filter(email=email).exists():
            return Response(
                 {"code": "USER_NOT_FOUND", "error": "User not registered"},
                status=400
            )

        # delete old OTPs
        EmailOTP.objects.filter(email=email).delete()

        otp = str(random.randint(100000, 999999))

        EmailOTP.objects.create(email=email, otp=otp)

        send_mail(
            "Your OTP",
            f"Your OTP is {otp}",
            "no-reply@example.com",
            [email],
        )

        return Response({"status": "OTP sent"})   

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP required"}, status=400)

        email = email.lower().strip()

        #  CHECK USER EXISTS (IMPORTANT)
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"error": "User not registered"},
                status=400
            )

        record = EmailOTP.objects.filter(email=email, otp=otp).last()

        if not record:
            return Response({"error": "Invalid OTP"}, status=400)

        # expiry check (5 minutes)
        if now() - record.created_at > timedelta(minutes=5):
            return Response({"error": "OTP expired"}, status=400)

        # generate JWT
        refresh = RefreshToken.for_user(user)

        # delete OTP after use
        record.delete()

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "no_org": not bool(user.current_organisation)
        })

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            token = request.data.get("token")

            if not token:
                return Response({"error": "Token required"}, status=status.HTTP_400_BAD_REQUEST)

            # Verify token with Google
            google_response = requests.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            )

            if google_response.status_code != 200:
                return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

            data = google_response.json()

            # Extract user info
            email = data.get("email")
            full_name = data.get("name")
            given_name = data.get("given_name")
            picture = data.get("picture")

            if not email:
                return Response({"error": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)

            # Decide display name
            display_name = given_name or full_name or ""

            # Create or get user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "role": "candidate",
                    "name": display_name   # ✅ use name field
                }
            )

            # Update existing user if name missing
            updated = False

            if not user.name and display_name:
                user.name = display_name
                updated = True

            # Optional: store profile picture
            if hasattr(user, "profile_picture") and picture:
                if not user.profile_picture:
                    user.profile_picture = picture
                    updated = True

            if updated:
                user.save()

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            # Response
            response_data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),

                # identity for frontend
                "email": user.email,
                "name": user.name or user.email, 
                "picture": picture,
            }

            # Organisation logic
            org = getattr(user, "current_organisation", None)

            if org:
                membership = org.members.filter(user=user, is_active=True).first()
                response_data.update({
                    "org_slug": org.slug,
                    "org_name": org.name,
                    "org_plan": org.plan,
                    "org_role": membership.role if membership else None
                })
            else:
                response_data["no_org"] = True

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print("GOOGLE ERROR:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )