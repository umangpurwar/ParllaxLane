from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from django.contrib.auth import authenticate, get_user_model


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "password", "name"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        name = validated_data.get("name", "")

        user = User.objects.create_user(
            username=email, 
            email=email,
            password=password
        )

        user.role = "candidate"
        user.name = name   
        user.save()

        return user

class CustomTokenSerializer(TokenObtainPairSerializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Find user by email only
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        # Authenticate using username internally (Django requirement)
        user = authenticate(
            username=user.username,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        # Generate token (still needs username internally)
        data = super().validate({
            "username": user.username,
            "password": password
        })

        # ===== org logic (unchanged) =====
        org = user.current_organisation

        if org:
            membership = org.members.filter(user=user, is_active=True).first()

            data["org_slug"] = org.slug
            data["org_name"] = org.name
            data["org_plan"] = org.plan
            data["org_role"] = membership.role if membership else None
        else:
            data["org_slug"] = None
            data["org_name"] = None
            data["org_plan"] = None
            data["org_role"] = None

        return data