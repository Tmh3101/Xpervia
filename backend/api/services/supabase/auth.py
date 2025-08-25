from .client import supabase
from api.models import User
from api.enums import RoleEnum

def create_user_metadata(data):
    return {
        "email": data.get("email"),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "role": RoleEnum.STUDENT.name,
    }

def register(email: str, password: str, first_name: str, last_name: str, date_of_birth: str) -> User:
    """
    Đăng ký người dùng mới trong Supabase Auth.
    """
    if User.objects.filter(email=email).exists():
        raise Exception("Email is already registered")

    user_metadata = create_user_metadata({
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth
    })

    data = {
        "email": email,
        "password": password,
        "options": {
            "data": user_metadata
        }
    }

    try:
        response = supabase.auth.sign_up(data)
    except Exception as e:
        raise e

    # Create User and save to database
    user = User(
        id=response.user.id, # Get user ID from Supabase response
        email=email,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth
    )
    user.save()

    return user


def login(email: str, password: str) -> dict:
    """
    Đăng nhập người dùng vào Supabase Auth.
    """

    if not User.objects.filter(email=email).exists():
        raise Exception("Email chưa được đăng ký")

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except Exception as e:
        if "Invalid login credentials" in str(e):
            raise Exception("Mật khẩu không chính xác")
        if "Email not confirmed" in str(e):
            raise Exception("Email chưa được xác nhận")
        raise e

    user = User.objects.get(id=response.user.id)
    access_token = response.session.access_token
    refresh_token = response.session.refresh_token

    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token
    }


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
        raise e
    
    user = User.objects.get(id=response.user.id)
    access_token = response.session.access_token
    refresh_token = response.session.refresh_token

    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def request_reset_password_view(email: str, redirect_url: str) -> None:
    """
    Khôi phục mật khẩu người dùng trong Supabase Auth.
    """
    try:
        supabase.auth.reset_password_for_email(
            email,
            {
                "redirect_to": redirect_url,
            }
        )
    except Exception as e:
        raise Exception(f"Error during Supabase password reset: {e}")
    

def reset_password(email: str, new_password: str) -> None:
    """
    Đặt lại mật khẩu người dùng trong Supabase Auth.
    """
    try:
        supabase.auth.update_user({
            "email": email,
            "password": new_password
        })
    except Exception as e:
        raise Exception(f"Error during Supabase password reset: {e}")
