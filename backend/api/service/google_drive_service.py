from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from django.conf import settings

def get_drive_service():
    """Tạo Google Drive API service"""
    creds = Credentials.from_authorized_user_info(
        {
            "client_id": settings.GOOGLE_DRIVE_CREDENTIALS["client_id"],
            "client_secret": settings.GOOGLE_DRIVE_CREDENTIALS["client_secret"],
            "refresh_token": settings.GOOGLE_DRIVE_CREDENTIALS["refresh_token"],
        }
    )
    return build("drive", "v3", credentials=creds)

def upload_file_to_drive(file_path, file_name):
    """Upload file lên Google Drive"""
    service = get_drive_service()
    
    file_metadata = {
        "name": file_name,
        "parents": [settings.GOOGLE_DRIVE_CREDENTIALS["folder_id"]],  # Hoặc thư mục Drive ID
    }
    media = MediaFileUpload(file_path, mimetype="image/jpeg")

    uploaded_file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    
    return uploaded_file.get("id")

def delete_file_from_drive(file_id):
    """Xóa file từ Google Drive"""
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()
