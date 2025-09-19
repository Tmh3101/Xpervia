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
    Existed
)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        return Response({
            'success': False,
            'message': 'Authentication failed',
            'error': exc.args
        }, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, NotFound):
        return Response({
            'success': False,
            'message': 'Not found',
            'error': exc.args
        }, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, PermissionDenied):
        return Response({
            'success': False,
            'message': 'Permission denied',
            'error': exc.args if exc.args else 'You do not have permission to perform this action'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if isinstance(exc, ValidationError):
        # Lấy lỗi đầu tiên từ exc.detail
        first_error = None
        if isinstance(exc.detail, dict):
            for key, value in exc.detail.items():
                if isinstance(value, list) and value:
                    first_error = value[0]
                    break
        elif isinstance(exc.detail, list) and exc.detail:
            first_error = exc.detail[0]
        
        return Response({
            'success': False,
            'message': 'Validation error',
            'error': first_error if first_error else exc.args
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, FileUploadException):
        return Response({
            'success': False,
            'message': 'File upload failed',
            'error': exc.args
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, Existed):
        return Response({
            'success': False,
            'message': 'Existed',
            'error': exc.args
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if response is None:
        return Response({
            'success': False,
            'message': 'Internal server error',
            'error': exc.args
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response