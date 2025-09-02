from django.db import models
from .course_content_model import CourseContent
from .chapter_model import Chapter
from .file_model import File


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    video_path = models.CharField(max_length=100)
    subtitle_vi_path = models.CharField(max_length=100, blank=True, null=True)
    attachment = models.OneToOneField(File, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name="lesson")
    course_content = models.ForeignKey(CourseContent, on_delete=models.CASCADE, related_name="lessons")
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name="lessons")
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
