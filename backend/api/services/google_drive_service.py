import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from django.conf import settings

# ID của thư mục chứa file trên Google Drive
GOOGLE_DRIVE_FOLDER_ID='1sfLAm55cBLc5NZcreEZjslcuhkCXSiIv'

# Đường dẫn đến file JSON chứa thông tin Service Account
SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, "api\\services\\service_account.json")

# Tạo credentials từ Service Account
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
)

# Tạo kết nối với Google Drive API
service = build("drive", "v3", credentials=creds)

def upload_file_to_drive(file_path, file_name):
    """Upload file lên Google Drive"""
    file_metadata = {
        "name": file_name,
        "parents": [GOOGLE_DRIVE_FOLDER_ID],  # Đặt thư mục chứa file trên Drive
    }
    media = MediaFileUpload(file_path, resumable=True)

    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return file.get("id")

def delete_file_from_drive(file_id):
    """Xóa file trên Google Drive"""
    service.files().delete(fileId=file_id).execute()

# Upload file method for calling
def upload_file(file):
    try:
        # Tạo thư mục tạm nếu nó không tồn tại
        temp_dir = "api\\services\\temp"

        # Save the file temporarily on the server
        file_path = os.path.join(temp_dir, file.name)
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Upload the file to Google Drive
        file_id = upload_file_to_drive(file_path, file.name)
    except Exception as e:
        raise Exception(f"Error uploading file: {str(e)}")
    finally:
        # Remove the file after uploading
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError as e:
                print(f"Error deleting file: {str(e)}")
    return file_id

# Delete file method for calling
def delete_file(file_id):
    try:
        delete_file_from_drive(file_id)
    except Exception as e:
        raise Exception(f"Error deleting file: {str(e)}")