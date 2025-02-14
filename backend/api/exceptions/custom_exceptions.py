from rest_framework.exceptions import APIException

class FileUploadException(APIException):
    status_code = 400
    default_detail = 'File upload failed'
    default_code = 'file_upload_failed'

class Existed(APIException):
    status_code = 400
    default_detail = 'Existed'
    default_code = 'existed'

class LoginFailed(APIException):
    status_code = 400
    default_detail = 'Login failed'
    default_code = 'login_failed'