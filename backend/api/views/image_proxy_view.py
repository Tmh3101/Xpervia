import requests
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from django.conf import settings

class ImageProxyView(GenericAPIView):
    permission_classes = [AllowAny]  # Có thể chỉnh lại nếu muốn bảo mật

    def get(self, request, file_id):
        GOOGLE_DRIVE_API_KEY = settings.GOOGLE_DRIVE_API_KEY
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={GOOGLE_DRIVE_API_KEY}"
        
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', 'image/jpeg')
                return HttpResponse(response.content, content_type=content_type)
            return HttpResponse(f"Failed to fetch image: {response.status_code}", status=response.status_code)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
