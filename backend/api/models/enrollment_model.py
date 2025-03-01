from django.db import models
from .payment_model import Payment
from .user_model import User
from .course_model import Course


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    created_at = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)

    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'

    def __str__(self):
        return f'{self.course.course_content.title} - {self.student.user.email}'