from django.db import models
from .user_model import User
from .category_model import Category


class CourseContent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail_id = models.CharField(max_length=50, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})

    categories = models.ManyToManyField(Category, related_name='course_contents')

    class Meta:
        db_table = 'course_contents'
        verbose_name = 'Course Content'
        verbose_name_plural = 'Course Contents'

    def __str__(self):
        return self.title