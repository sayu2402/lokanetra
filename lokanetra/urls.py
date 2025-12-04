"""
Main URL configuration for the Lokanetra project.

This file connects:
- Django admin panel
- User & OTP routes
- Wallet routes
- Transaction routes
- Swagger and ReDoc API documentation
"""

from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Swagger / API documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="Lokanetra API",
        default_version="v1",
        description="API for OTP login + wallet + transactions",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django admin panel
    path("admin/", admin.site.urls),
    # User & OTP-related endpoints
    path("auth/", include("users.urls")),
    # Wallet operations
    path("wallet/", include("wallet.urls")),
    # Transaction-related admin endpoints
    path("transactions/", include("transactions.urls")),
    # Swagger JSON schema
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    # Swagger UI documentation
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # ReDoc documentation UI
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
