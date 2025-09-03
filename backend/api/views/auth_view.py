import logging
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from api.services.supabase import auth
from api.models import User
from api.serializers import UserSerializer


logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    date_of_birth = request.data.get("date_of_birth")
    role = request.data.get("role")

    logger.info(f"Registering user with email: {email}")

    try:
        user = auth.register(email, password, first_name, last_name, date_of_birth, role)
    except Exception as e:
        logger.error(f"Error during Supabase registration: {e}")
        return Response({
            "success": False,
            "message": "Registration failed",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

    logger.info(f"User registered successfully: {user.email}")
    return Response({
        "success": True,
        "message": "Registration successful",
        "user": UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    logger.info(f"Logging in user with email: {email}")

    try:
        result = auth.login(email, password)
    except Exception as e:
        logger.error(f"Error during Supabase login: {e}")
        return Response({
            "success": False,
            "message": "Login failed",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

    logger.info(f"User logged in successfully: {result['user'].email}")
    return Response({
        "success": True,
        "message": "Login successful",
        "access_token": result['access_token'],
        "refresh_token": result['refresh_token'],
        "user": UserSerializer(result['user']).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_session_view(request):
    refresh_token = request.data.get("refresh_token")
    try:
        result = auth.refresh_session(refresh_token)
    except Exception as e:
        logger.error(f"Error during session refresh: {e}")
        raise AuthenticationFailed(e)
    
    return Response({
        "success": True,
        "message": "Session refreshed successfully",
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "user": UserSerializer(result["user"]).data
    }, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_reset_password_view(request):
    email = request.data.get("email")
    redirect_url = request.data.get("redirect_url")

    try:
        if not User.objects.filter(email=email).exists():
            raise Exception("Email chưa được đăng ký")

        auth.request_reset_password_view(email, redirect_url)
    except Exception as e:
        logger.error(e)
        raise AuthenticationFailed(e)

    return Response({
        "success": True,
        "message": "Password reset email sent successfully"
    }, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password_view(request):
    email = request.user.email
    new_password = request.data.get("new_password")

    if not email or not new_password:
        return Response({
            "success": False,
            "message": "Email and new password are required"
        }, status=400)

    try:
        auth.reset_password(email, new_password)
    except Exception as e:
        logger.error(e)
        raise AuthenticationFailed(e)

    return Response({
        "success": True,
        "message": "Password reset successfully"
    }, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    try:
        user = request.user
        print(f"Current user: {user}")
    except Exception as e:
        logger.error(f"Error retrieving user info: {e}")
        return Response({
            "success": False,
            "message": "Failed to retrieve user info",
            "error": str(e)
        }, status=400)
    
    logger.info(f"User info retrieved successfully: {user.email}")  
    return Response({
        "success": True,
        "message": "User info retrieved successfully",
        "user": UserSerializer(user).data,
    }, status=200)

