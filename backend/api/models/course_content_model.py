from django.db import models
from .category_model import Category


class CourseContent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail_id = models.CharField(max_length=50, null=True, blank=True)
    teacher_id = models.UUIDField()
    categories = models.ManyToManyField(Category, related_name='course_contents')

    class Meta:
        db_table = 'course_contents'
        verbose_name = 'Course Content'
        verbose_name_plural = 'Course Contents'

    def __str__(self):
        return self.title