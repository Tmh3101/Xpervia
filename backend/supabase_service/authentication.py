import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from .auth import get_user_info_by_id

SUPABASE_JWT_SECRET = getattr(settings, 'SUPABASE_JWT_SECRET')

class SupabaseJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # Không cung cấp token thì bỏ qua, không raise lỗi

        token = auth_header.split(' ')[1]

        try:
            # Giải mã token
            decoded = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",  # <-- Thêm dòng này để khớp với "aud" trong token
            )
            user_id = decoded.get('sub')  # Supabase UID

            if not user_id:
                raise AuthenticationFailed('User ID (sub) not found in token')

            # Lấy thông tin user từ Supabase
            user = get_user_info_by_id(user_id)
            if not user:
                raise AuthenticationFailed('User not found')
            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')