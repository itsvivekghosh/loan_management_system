from django.db import models
from loan.models import Loan
import uuid
from datetime import datetime


class Payments(models.Model):
    '''
    Payment Model
    '''
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.PositiveBigIntegerField(null=False, blank=False)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    loan_paid_for_month_number = models.IntegerField(blank=True)
    loan_paid_month = models.DateField(null=True, blank=True)
    principal_amount = models.BigIntegerField(blank=True, null=True)
    payment_timestamp = models.DateTimeField(default=datetime.utcnow())
    interest_paid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'payments'