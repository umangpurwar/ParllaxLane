from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]  
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"]
        )

        # FORCE SAFE DEFAULT
        user.role = "candidate"
        user.save()

        return user

class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
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