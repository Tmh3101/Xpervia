from django.db import models
from .course_model import Course
from django.utils import timezone

class CourseDetail(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    discount = models.FloatField(default=0)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    regis_start_date = models.DateTimeField(default=timezone.now)
    regis_end_date = models.DateTimeField()
    max_students = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'course_details'
        verbose_name = 'CourseDetail'
        verbose_name_plural = 'CourseDetails'

    def __str__(self):
        return f'{self.course.id} - {self.price}'