from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        source="userprofile.phone_number", allow_blank=True
    )

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "phone_number")
        read_only_fields = ("id", "username")
