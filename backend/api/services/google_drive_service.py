import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from django.conf import settings
from django.core.files.storage import default_storage

# Get Google Drive API service method
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

# Upload file to Google Drive method
def upload_file_to_drive(file_path, file_name):
    service = get_drive_service()
    
    file_metadata = {
        "name": file_name,
        "parents": [settings.GOOGLE_DRIVE_CREDENTIALS["folder_id"]], # Folder ID to upload file to
    }
    media = MediaFileUpload(file_path, mimetype="image/jpeg")

    uploaded_file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    
    return uploaded_file.get("id")

# Delete file from Google Drive method
def delete_file_from_drive(file_id):
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()

# Upload file method for calling
def upload_file(file):
    try:
        # Save the thumbnail file temporarily on the server
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Upload the thumbnail file to Google Drive
        file_id = upload_file_to_drive(file_path, file.name)
    except Exception as e:
        raise Exception("Error uploading file to Google Drive")
    
    # Remove the temporary file
    os.remove(file_path)
    return file_id

# Delete file method for calling
def delete_file(file_id):
    try:
        delete_file_from_drive(file_id)
    except Exception as e:
        raise Exception("Error deleting file from Google Drive")

