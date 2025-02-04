from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail_id = models.CharField(max_length=255, null=True, blank=True)
    price = models.IntegerField(default=0)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    regis_start_date = models.DateTimeField()
    regis_end_date = models.DateTimeField()
    max_students = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title