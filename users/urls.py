from django.urls import path

from .views import SendOTPView, UserListAdminView, VerifyOTPView

urlpatterns = [
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("admin/users/", UserListAdminView.as_view(), name="admin-users"),
]
