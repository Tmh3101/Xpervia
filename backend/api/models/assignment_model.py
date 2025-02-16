from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from .lesson_model import Lesson


class Assignment(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    start_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'assignments'
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'

    def clean(self):
        if self.start_at <= self.lesson.created_at:
            raise ValidationError('Start time must be greater than the lesson creation time.')

        if self.start_at > self.due_at:
            raise ValidationError('Start date must be before due date')
        
    def __str__(self):
        return self.title