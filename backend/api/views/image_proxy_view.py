import mimetypes
import logging
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.services.google_drive_service import download_file_from_drive
from django.http import HttpResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ImageProxyView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        file_id = self.kwargs.get('file_id')
        logger.info(f"Fetching image with file ID: {file_id}")
        if not file_id:
            logger.error("Missing file_id in request")
            return Response({
                'success': False,
                'message': 'Missing file_id',
            }, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"drive_image_{file_id}"
        try:
            cached_image = cache.get(cache_key)
        except Exception as e:
            logger.error(f"Error accessing cache for file ID: {file_id} - {str(e)}")
            return Response({
                'success': False,
                'message': 'Error accessing cache',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if cached_image:
            logger.info(f"[CACHE HIT] Retrieved image for file ID: {file_id}")
            return HttpResponse(cached_image['content'], content_type=cached_image['content_type'])

        try:
            image_bytes = download_file_from_drive(file_id)
            content_type, _ = mimetypes.guess_type(f"{file_id}.jpg")
            content_type = content_type or 'application/octet-stream'

            # Cache ảnh trong 6 tiếng
            cache.set(cache_key, {
                'content': image_bytes,
                'content_type': content_type
            }, timeout=60 * 60 * 6)

            logger.info(f"[CACHE MISS] Downloaded image for file ID: {file_id} from Google Drive")
            return HttpResponse(image_bytes, content_type=content_type)

        except Exception as e:
            logger.error(f"Error downloading file from Google Drive for file ID: {file_id} - {str(e)}")
            return Response({
                'success': False,
                'message': 'Error downloading file from Google Drive',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
