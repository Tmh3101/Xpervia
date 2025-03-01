from django.db import models
from .course_content_model import CourseContent


class Chapter(models.Model):
    title = models.CharField(max_length=255)
    course_content = models.ForeignKey(CourseContent, on_delete=models.CASCADE, related_name='chapters')
    order = models.IntegerField()

    class Meta:
        ordering = ['order']
        db_table = 'chapters'
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'

    def __str__(self):
        return self.title