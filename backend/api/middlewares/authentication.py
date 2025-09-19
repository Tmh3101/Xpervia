import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from api.models import User
from django.apps import apps as django_apps

SUPABASE_JWT_SECRET = getattr(settings, 'SUPABASE_JWT_SECRET')
SUPABASE_AUD = "authenticated"  # khớp với "aud" trong token
JWT_LEEWAY_SECONDS = 600        # ví dụ: cho phép lệch 10 phút

class UserAuthenticated:
    def __init__(self, user_data):
        self.id = user_data.id
        self.email = user_data.email
        self.first_name = user_data.first_name
        self.last_name = user_data.last_name
        self.date_of_birth = user_data.date_of_birth
        self.avatar_url = user_data.avatar_url
        self.role = user_data.role
        self.is_active = user_data.is_active
        self.created_at = user_data.created_at
        self.updated_at = user_data.updated_at
        self.is_authenticated = True  # Đánh dấu người dùng đã xác thực

class SupabaseJWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith(f"{self.keyword} "):
            return None

        token = auth.split(" ", 1)[1]
        if not SUPABASE_JWT_SECRET:
            raise AuthenticationFailed("Server missing SUPABASE_JWT_SECRET")

        try:
            # Không sửa iat/exp — chỉ dùng leeway
            claims = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience=SUPABASE_AUD,     # khớp aud
                leeway=JWT_LEEWAY_SECONDS, # cho phép lệch thời gian
                options={
                    "require": ["exp", "iat", "aud", "sub"],
                },
            )
        except ExpiredSignatureError:
            raise AuthenticationFailed("Token đã hết hạn")
        except InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {e}")

        user_id = claims.get('sub')  # Supabase UID

        if not user_id:
            raise AuthenticationFailed("Thiếu sub trong token")

         # Lấy model động để tránh AppRegistryNotReady khi import sớm
        User = django_apps.get_model("api", "User")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User không tồn tại trong hệ thống")
        
        if not user:
            raise AuthenticationFailed("Người dùng không tồn tại")

        user_auth = UserAuthenticated(user)
        return (user_auth, token)