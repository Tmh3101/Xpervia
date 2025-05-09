"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from supabase_service import auth_view
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from supabase_service.file_url_view import FileAccessURLAPIView

schema_view = get_schema_view(
   openapi.Info(
      title="Xpervia API",
      default_version='v1',
      description="Tài liệu các endpoint API cho hệ thống LMS Xpervia",
      contact=openapi.Contact(email="your-email@example.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django Admin URLs
    path("admin/", admin.site.urls),

    # Authentication URLs
    path('auth/register/', auth_view.register_view, name='register'),
    path('auth/login/', auth_view.login_view, name='login'),
    path('auth/logout/', auth_view.logout_view, name='logout'),
    path('auth/refresh/', auth_view.refresh_session_view, name='refresh-session'),
    path('auth/current-user/', auth_view.get_current_user, name='current-user'),
    
    # Coures URLs
    path("api/", include("api.urls")), 

    # Signed URL for Supabase
    path('files/access-url/', FileAccessURLAPIView.as_view(), name='file-access-url'),

    # Swagger and Redoc URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
