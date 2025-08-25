import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from api.models import User

SUPABASE_JWT_SECRET = getattr(settings, 'SUPABASE_JWT_SECRET')

class UserAuthenticated(User):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_authenticated = True

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
            user = User.objects.get(id=user_id)
            if not user:
                raise AuthenticationFailed('User not found')
            
            user_dict = user.__dict__
            del user_dict['_state']  # Xóa trường _state để tránh lỗi khi tạo instance mới

            user_auth = UserAuthenticated(**user_dict)
            return (user_auth, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')