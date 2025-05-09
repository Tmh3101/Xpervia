from supabase import create_client
from django.conf import settings
from types import SimpleNamespace
from .user_metadata import UserMetadataService

# Tạo client Supabase
supabase = create_client(settings.SUPABASE_PROJECT_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

class SupabaseUser:
    def __init__(self, id, email, phone, created_at, updated_at, last_sign_in_at, is_authenticated, user_metadata):
        self.id = id
        self.email = email
        self.phone = phone
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_sign_in_at = last_sign_in_at
        self.is_authenticated = is_authenticated
        self.user_metadata = SimpleNamespace(**user_metadata)

    def __str__(self):
        return f"SupabaseUser(id={self.id}, email={self.email})"
    
    def to_dict(self):
        user_metadata_dict = vars(self.user_metadata) if self.user_metadata else {}
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_sign_in_at": self.last_sign_in_at.isoformat() if self.last_sign_in_at else None,
            "is_authenticated": self.is_authenticated,
            "user_metadata": user_metadata_dict
        }

# Lấy thông tin người dùng từ object Supabase user
def get_supabase_user_info(user: dict) -> SupabaseUser:
    return SupabaseUser(
        id=user.id,
        email=user.email,
        phone=user.phone,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_sign_in_at=user.last_sign_in_at,
        is_authenticated=user.aud == "authenticated",
        user_metadata=user.user_metadata
    )


def register(email: str, password: str, user_metadata: dict = None) -> SupabaseUser:
    """
    Đăng ký người dùng mới trong Supabase Auth.
    """
    validated_metadata = UserMetadataService.create_metadata(user_metadata)
    data = {
        "email": email,
        "password": password,
        "options": {
            "data": validated_metadata
        }
    }

    try:
        response = supabase.auth.sign_up(data)
    except Exception as e:
        raise Exception(f"Error during Supabase registration: {e}")
    
    return get_supabase_user_info(response.user)


def login(email: str, password: str) -> dict:
    """
    Đăng nhập người dùng vào Supabase Auth.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except Exception as e:
        raise Exception(f"Error during Supabase login: {e}")
    
    return response


def logout(token) -> bool:
    """
    Đăng xuất người dùng khỏi Supabase Auth.
    """
    try:
        response = supabase.auth.sign_out(token)
        return response.status_code == 200
    except Exception as e:
        raise Exception(f"Error during Supabase logout: {e}")
    

def refresh_session(refresh_token: str) -> dict:
    """
    Làm mới session bằng refresh_token.
    """
    try:
        response = supabase.auth.refresh_session(refresh_token)
    except Exception as e:
        raise Exception(f"Error refreshing session: {e}")
    return response


def get_user_info_by_id(user_id: str) -> SupabaseUser:
    """
    Lấy thông tin người dùng từ Supabase Auth bằng ID.
    """
    try:
        response = supabase.auth.admin.get_user_by_id(user_id)
    except Exception as e:
        print(f"Error getting user info by ID: {e}")
    if response and response.user:
        return get_supabase_user_info(response.user)
    return None


def get_all_users() -> list:
    """
    Trả về danh sách tất cả người dùng từ Supabase Auth.
    """
    response = supabase.auth.admin.list_users()
    if response:
        return [get_supabase_user_info(user) for user in response]
    return []


def get_user_info_by_token(token) -> SupabaseUser:
    try:
        response = supabase.auth.get_user(token)
    except Exception as e:
        raise Exception(f"Error getting user info by token: {e}")
    return get_supabase_user_info(response.user)


def update_user_info_by_id(user_id: str, email: str, password: str, user_metadata: dict) -> SupabaseUser:
    """
    Cập nhật thông tin người dùng trong Supabase Auth.
    """

    update_data = {
        "email": email,
        "password": password,
        "user_metadata": UserMetadataService.create_metadata(user_metadata)
    }

    response = supabase.auth.admin.update_user_by_id(user_id, update_data)
    if response and response.user:
        return get_supabase_user_info(response.user)
    return None


def update_user_metadata(user_id: str, metadata: dict) -> bool:
    """
    Cập nhật user_metadata cho người dùng.
    """
    response = supabase.auth.admin.update_user_by_id(user_id, {
        "user_metadata": metadata
    })
    return bool(response and response.user)


def delete_user(user_id: str) -> None:
    """
    Xóa người dùng khỏi Supabase Auth.
    """
    try:
        supabase.auth.admin.delete_user(user_id)
    except Exception as e:
        raise Exception(f"Error deleting user: {e}")


def create_user(email: str, password: str, user_metadata: dict = None) -> SupabaseUser:
    """
    Tạo người dùng mới trong Supabase Auth.
    """
    validated_metadata = UserMetadataService.create_metadata(user_metadata)
    data = {
        "email": email,
        "email_confirm": True,
        "password": password,
        "user_metadata": validated_metadata
    }

    response = supabase.auth.admin.create_user(data)
    if response and response.user:
        return get_supabase_user_info(response.user)
    return None
