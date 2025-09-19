from django.db import models
from api.enums import RoleEnum
import uuid

ROLE_CHOICES = [(role.value, role.name) for role in RoleEnum]

class User(models.Model):
    # id reference user_id in supabase auth
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Cache thuận tiện truy vấn; Supabase Auth là nguồn gốc
    email = models.EmailField(unique=True, db_index=True)

    # Hồ sơ nghiệp vụ trong app
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar_url = models.URLField(blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=RoleEnum.STUDENT.name)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email