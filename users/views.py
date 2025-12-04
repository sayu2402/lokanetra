"""
This file handles OTP login and user creation.
It includes:
- Sending OTP
- Verifying OTP
- Creating user + wallet if new
- Admin: list all users
"""

import random

from django.contrib.auth.models import User
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from wallet.models import Wallet

from .models import OTP, UserProfile
from .serializers import SendOTPSerializer, UserSerializer, VerifyOTPSerializer


def _generate_otp(length=6):
    """
    Generate a random OTP with the given number of digits.
    """
    return "".join(str(random.randint(0, 9)) for _ in range(length))


class SendOTPView(APIView):
    """
    Send OTP to a phone number.
    For this test, OTP is returned in the response.
    """

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=SendOTPSerializer, responses={201: SendOTPSerializer()}
    )
    def post(self, request):
        """
        Validate phone number and create an OTP entry.
        """
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        code = _generate_otp(4)

        OTP.objects.create(phone_number=phone, code=code)

        return Response(
            {"phone_number": phone, "otp": code}, status=status.HTTP_201_CREATED
        )


class VerifyOTPView(APIView):
    """
    Verify the OTP entered by the user.
    If OTP is correct, return JWT tokens.
    If user is new, create user and wallet.
    """

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=VerifyOTPSerializer, responses={200: "token"})
    def post(self, request):
        """
        Check OTP validity and log the user in.
        """
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["otp"]

        # Find valid OTP
        try:
            otp_obj = OTP.objects.filter(
                phone_number=phone, code=code, is_used=False
            ).latest("created_at")
        except OTP.DoesNotExist:
            return Response(
                {"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiry
        if otp_obj.is_expired():
            return Response(
                {"detail": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj.is_used = True
        otp_obj.save()

        # Create user if not exists
        with transaction.atomic():
            profile_qs = UserProfile.objects.filter(phone_number=phone).select_related(
                "user"
            )

            if profile_qs.exists():
                user = profile_qs.first().user
            else:
                username = f"user_{phone}"
                user = User.objects.create(username=username)
                UserProfile.objects.filter(user=user).update(phone_number=phone)
                Wallet.objects.create(user=user)

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "phone_number": phone,
                },
            }
        )


class UserListAdminView(generics.ListAPIView):
    """
    Admin endpoint to list all users.
    """

    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
