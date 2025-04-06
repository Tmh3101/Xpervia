from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from api.enums import RoleEnum
import uuid

# Create UserManager class to set email as username field
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser must have role=admin.')

        return self.create_user(email, password, **extra_fields)

# Create User model with email as username field, add role field, and set id is a uuid field
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True, max_length=255)
    date_of_birth = models.DateField(null=True, blank=True, default=None)

    ROLE_CHOICES = [(role.name, role.description) for role in RoleEnum]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=RoleEnum.STUDENT.name)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


    def __str__(self):
        return self.email
