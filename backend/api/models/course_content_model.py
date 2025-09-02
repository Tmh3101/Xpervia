from django.db import models
from .category_model import Category
from .user_model import User


class CourseContent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail_path = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher')
    categories = models.ManyToManyField(Category, related_name='course_contents')

    class Meta:
        db_table = 'course_contents'
        verbose_name = 'Course Content'
        verbose_name_plural = 'Course Contents'

    def __str__(self):
        return self.title