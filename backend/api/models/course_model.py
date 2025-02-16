from django.db import models
from .user_model import User
from .category_model import Category


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail_id = models.CharField(max_length=50, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})

    categories = models.ManyToManyField(Category, related_name='courses')

    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return self.title