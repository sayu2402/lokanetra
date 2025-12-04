"""
This file contains serializers used for:
- Sending OTP
- Verifying OTP
- Returning user details
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class SendOTPSerializer(serializers.Serializer):
    """
    Serializer for sending OTP.
    Only takes a phone number from the user.
    """
    phone_number = serializers.CharField(max_length=15)


class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying OTP.
    Requires phone number and the 4/6 digit OTP.
    """
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for returning user information.
    Includes username, basic details,
    and phone number from the UserProfile model.
    """
    phone_number = serializers.CharField(
        source="userprofile.phone_number",
        allow_blank=True,
        help_text="User's registered phone number.",
    )

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "phone_number")
        read_only_fields = ("id", "username")
