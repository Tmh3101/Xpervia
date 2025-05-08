import logging
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from supabase_service.auth import (
    register, login, logout, get_supabase_user_info, get_user_info_by_token, refresh_session
)
from supabase_service.user_metadata import UserMetadataService


logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    email = request.data.get("email")
    password = request.data.get("password")
    metadata = request.data.get("user_metadata", {})

    # Validate metadata
    validated_metadata = UserMetadataService.create_metadata(metadata)
    logger.info(f"Registering user with email: {email} and metadata: {validated_metadata}")

    try:
        user = register(email, password, validated_metadata)
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
        "user": user.to_dict()
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    logger.info(f"Logging in user with email: {email}")

    try:
        result = login(email, password)
    except Exception as e:
        logger.error(f"Error during Supabase login: {e}")
        return Response({
            "success": False,
            "message": "Login failed",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

    user = get_supabase_user_info(result.session.user)
    logger.info(f"User logged in successfully: {user.email}")
    return Response({
        "success": True,
        "message": "Login successful",
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "user": user.to_dict()
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_view(request):
    token = request.headers.get('Authorization', '').replace("Bearer ", "")
    if not token:
        logger.error("Logout failed: No access token provided")
        return Response({
            "success": False,
            "message": "No access token provided"
        }, status=400)

    result = logout(token)
    if not result:
        logger.error("Logout failed: No result returned")
        return Response({
            "success": False,
            "message": "Logout failed",
        }, status=400)
    
    logger.info(f"User logged out successfully: {request.user.email}")
    return Response({
        "success": True,
        "message": "Logged out successfully"
    }, status=200)


@api_view(['POST'])
def refresh_session_view(request):
    refresh_token = request.data.get("refresh_token")
    try:
        result = refresh_session(refresh_token)
    except Exception as e:
        return Response({
            "success": False,
            "message": "Failed to refresh session",
            "error": str(e)
        }, status=401)
    
    return Response({
        "success": True,
        "message": "Session refreshed successfully",
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "user": get_supabase_user_info(result.session.user).to_dict()
    }, status=200)


@api_view(['GET'])
def get_current_user(request):
    token = request.headers.get('Authorization', '').replace("Bearer ", "")
    if not token:
        return Response({
            "success": False,
            "message": "No access token provided"
        }, status=400)
    
    try:
        user = get_user_info_by_token(token)
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
        "user": user.to_dict(),
    }, status=200)
