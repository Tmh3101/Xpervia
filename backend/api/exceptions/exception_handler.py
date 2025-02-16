from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
    AuthenticationFailed
)
from .custom_exceptions import (
    FileUploadException,
    Existed,
    LoginFailed
)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        return Response({
            'success': False,
            'message': 'Authentication failed',
            'errors': exc.args
        }, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, NotFound):
        return Response({
            'success': False,
            'message': 'Not found',
            'errors': exc.args
        }, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, PermissionDenied):
        return Response({
            'success': False,
            'message': 'Permission denied',
            'errors': exc.args if exc.args else 'You do not have permission to perform this action'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if isinstance(exc, ValidationError):
        return Response({
            'success': False,
            'message': 'Validation error',
            'errors': exc.args
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, FileUploadException):
        return Response({
            'success': False,
            'message': 'File upload failed',
            'errors': exc.args
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, Existed):
        return Response({
            'success': False,
            'message': 'Existed',
            'errors': exc.args
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, LoginFailed):
        return Response({
            'success': False,
            'message': 'Login failed',
            'errors': exc.args
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if response is None:
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response