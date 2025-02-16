from django.db import models
from .assignment_model import Assignment
from .user_model import User


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'submissions'
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
    
    def __str__(self):
        return f'{self.assignment} - {self.student}'
    