from django.db import models
from api.models.course_model import Course
from api.models.chapter_model import Chapter

class Lesson(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=50)
    subtitle_vi_id = models.CharField(max_length=50, blank=True, null=True)
    attachment_id = models.CharField(max_length=50, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name="lessons")
    is_visible = models.BooleanField(default=True)
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        db_table = 'lessons'
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'

    def __str__(self):
        return self.title
