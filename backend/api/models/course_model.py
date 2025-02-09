from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .category_model import Category

User = get_user_model()

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='courses')
    thumbnail_id = models.CharField(max_length=50, null=True, blank=True)
    price = models.IntegerField(default=0)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(timezone.now)
    regis_start_date = models.DateTimeField(default=timezone.now)
    regis_end_date = models.DateTimeField()
    max_students = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.title