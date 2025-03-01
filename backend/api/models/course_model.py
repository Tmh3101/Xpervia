from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from .course_content_model import CourseContent


class Course(models.Model):
    course_content = models.OneToOneField(CourseContent, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    discount = models.FloatField(default=0)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(default=timezone.now)
    regis_start_date = models.DateTimeField(default=timezone.now)
    regis_end_date = models.DateTimeField(null=True, blank=True)
    max_students = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def clean(self):
        if self.start_date < self.course_content.created_at:
            raise ValidationError('Start date must be greater than the course content creation time.')

        if self.regis_start_date > self.regis_end_date:
            raise ValidationError('Registration start date must be before registration end date')
        
    def get_discounted_price(self):
        return self.price * (1 - self.discount)

    def __str__(self):
        return f'{self.course_content} - {self.start_date}'