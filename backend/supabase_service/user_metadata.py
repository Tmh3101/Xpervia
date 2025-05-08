from api.enums import RoleEnum


class UserMetadataSchema:
    DEFAULTS = {
        "role": RoleEnum.STUDENT.name,
        "is_active": True,
        "first_name": "",
        "last_name": "",
        "date_of_birth": None,
        "avatar_url": "",
        "email_verified": False,
        "phone_verified": False,
    }

    @staticmethod
    def validate(metadata: dict) -> dict:
        validated = UserMetadataSchema.DEFAULTS.copy()
        if not isinstance(metadata, dict):
            return validated
        for key in validated.keys():
            if key in metadata:
                validated[key] = metadata[key]
        return validated


class UserMetadataService:
    """
    Service để truy cập và cập nhật user_metadata trong Supabase Auth.
    """
    
    @staticmethod
    def create_metadata(data: dict) -> dict:
        validated = UserMetadataSchema.validate(data)
        return validated
