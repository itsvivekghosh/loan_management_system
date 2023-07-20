from django.db import models
from loan.models import Loan
import uuid, datetime


class Payments(models.Model):

    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.PositiveBigIntegerField(null=False, blank=False, default=0)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    loan_paid_for_month_number = models.IntegerField(blank=True)
    payment_timestamp = models.DateTimeField(default=datetime.date.today)