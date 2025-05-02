import os
from api.models import File
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from django.conf import settings
import requests
from requests.exceptions import SSLError, RequestException

# ID của thư mục chứa file trên Google Drive
GOOGLE_DRIVE_FOLDER_ID='1sfLAm55cBLc5NZcreEZjslcuhkCXSiIv'

# Đường dẫn đến file JSON chứa thông tin Service Account
SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, "api", "services", "service_account.json")

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
    return {'file_id': file.get("id"), 'file_name': file_name}

def delete_file_from_drive(file_id):
    """Xóa file trên Google Drive"""
    service.files().delete(fileId=file_id).execute()

def download_file_from_drive(file_id: str):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        response = session.get(url, headers=headers, stream=True, timeout=10)

        response.raise_for_status()
        return response
    except SSLError as e:
        print(f"[SSL ERROR] Google Drive: {e}")
        raise Exception("SSL error during file download.")
    except RequestException as e:
        print(f"[REQUEST ERROR] Google Drive: {e}")
        raise Exception("Request error during file download.")

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
        file = upload_file_to_drive(file_path, file.name)
    except Exception as e:
        raise Exception(f"Error uploading file: {str(e)}")
    finally:
        # Remove the file after uploading
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError as e:
                print(f"Error deleting file: {str(e)}")
    return file

# Delete file method for calling
def delete_file(file_id):
    try:
        delete_file_from_drive(file_id)
        file = File.objects.filter(file_id=file_id).first()
        if file:
            file.delete()
    except Exception as e:
        raise Exception(f"Error deleting file: {str(e)}")
    
