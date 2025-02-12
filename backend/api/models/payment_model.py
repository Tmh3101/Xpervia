from django.db import models
from api.enums.payment_status_enum import PaymentStatusEnum

class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.IntegerField()
    payment_method = models.CharField(max_length=50, null=True, default=None)
    status = models.CharField(
        max_length=10,
        choices=[(status.name, status.value) for status in PaymentStatusEnum],
        default=PaymentStatusEnum.COMPLETED.name
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f'{self.amount} - {self.payment_method}'