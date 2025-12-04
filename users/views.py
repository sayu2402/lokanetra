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
    return "".join(str(random.randint(0, 9)) for _ in range(length))


class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=SendOTPSerializer, responses={201: SendOTPSerializer()}
    )
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]

        code = _generate_otp(4)
        OTP.objects.create(phone_number=phone, code=code)
        return Response(
            {"phone_number": phone, "otp": code}, status=status.HTTP_201_CREATED
        )


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=VerifyOTPSerializer, responses={200: "token"})
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["otp"]

        try:
            otp_obj = OTP.objects.filter(
                phone_number=phone, code=code, is_used=False
            ).latest("created_at")
        except OTP.DoesNotExist:
            return Response(
                {"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.is_expired():
            return Response(
                {"detail": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj.is_used = True
        otp_obj.save()

        with transaction.atomic():
            profile_qs = UserProfile.objects.filter(phone_number=phone).select_related(
                "user"
            )
            if profile_qs.exists():
                profile = profile_qs.first()
                user = profile.user
            else:
                username = f"user_{phone}"
                user = User.objects.create(username=username)
                UserProfile.objects.filter(user=user).update(phone_number=phone)
                Wallet.objects.create(user=user)

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
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
