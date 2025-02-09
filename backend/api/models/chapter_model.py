from django.db import models
from api.models.course_model import Course

class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")
    order = models.IntegerField()

    class Meta:
        ordering = ['order']
        db_table = 'chapters'
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'

    def __str__(self):
        return self.title