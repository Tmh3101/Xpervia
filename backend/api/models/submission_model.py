from django.db import models
from .assignment_model import Assignment
from .user_model import User
from .file_model import File


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='submission')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'submissions'
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
    
    def __str__(self):
        return f'{self.assignment} - {self.student}'
    