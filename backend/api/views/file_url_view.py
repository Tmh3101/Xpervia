from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import status
from api.services.supabase.storage import get_file_url
import logging

logger = logging.getLogger(__name__)

class FileAccessURLAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bucket = request.query_params.get('bucket')
        path = request.query_params.get('path')
        is_public = request.query_params.get('is_public', 'false').lower() == 'true'

        if not bucket or not path:
            raise ValidationError("Both 'bucket' and 'path' are required.")

        try:
            url = get_file_url(bucket, path, is_public)
            if not url:
                logger.error(f"Failed to retrieve file URL for bucket: {bucket}, path: {path}")
                raise Exception("Failed to retrieve file URL")

            logger.info(f"{'Public' if is_public else 'Signed'} URL generated for: {path}")
            return Response({
                "success": True,
                "message": "File URL generated successfully",
                "url": url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating file URL: {str(e)}")
            return Response({
                "success": False,
                "message": f"Failed to generate file URL: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
