"""
URL routes for user and OTP-related operations.
Includes:
- sending OTP
- verifying OTP
- admin user listing
"""

from django.urls import path

from .views import SendOTPView, UserListAdminView, VerifyOTPView

urlpatterns = [
    # Send OTP to a phone number
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    # Verify OTP and log the user in
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    # Admin endpoint to list all users
    path("admin/users/", UserListAdminView.as_view(), name="admin-users"),
]
