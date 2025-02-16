from django.db import models
from api.enums import PaymentStatusEnum


class Payment(models.Model):
    amount = models.IntegerField()
    payment_method = models.CharField(max_length=50, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    PAYMENT_STATUS_CHOICES = [(status.name, status.value) for status in PaymentStatusEnum]
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=PaymentStatusEnum.COMPLETED.name)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f'{self.amount} - {self.payment_method}'