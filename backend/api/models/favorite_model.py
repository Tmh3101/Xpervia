from django.db import models
from .user_model import User
from .course_model import Course


class Favorite(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.email} - {self.course.course_content.title}"