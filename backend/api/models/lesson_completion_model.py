from django.db import models
from .lesson_model import Lesson
from .user_model import User


class LessonCompletion(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lesson_completions'
        verbose_name = 'Lesson Completion'
        verbose_name_plural = 'Lesson Completions'
        unique_together = ('lesson', 'student')
    
    def __str__(self):
        return f'{self.lesson} - {self.student}'