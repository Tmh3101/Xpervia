from django.db import models
from .submission_model import Submission


class SubmissionScore(models.Model):
    score = models.FloatField()
    feedback = models.TextField(null=True, blank=True)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='score')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'submission_scores'
        verbose_name = 'Submission Score'
        verbose_name_plural = 'Submission Scores'

    def __str__(self):
        return f'{self.submission} - {self.score}'