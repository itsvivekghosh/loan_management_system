from django.db import models
from user.models import User
import uuid

LOAN_CHOICES = (
    ("Car", "CAR"),
    ("Home", "HOME"),
    ("Education", "EDUCATION"),
    ("Personal", "PERSONAL"),
)

class Loan(models.Model):

    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(choices=LOAN_CHOICES, default="Personal", max_length=9)
    loan_amount = models.BigIntegerField()
    total_loan_amount_with_interest = models.BigIntegerField(blank=True)
    interest_rate = models.FloatField()
    term_period = models.IntegerField()
    disbursement_date = models.DateField()
    emi_amount = models.FloatField(blank=True)
    total_loan_amount_paid = models.FloatField(blank=True, default=0.0)
    emi_due_dates_with_payment_history = models.JSONField()

    def __str__(self) -> str:
        return '{} -> {}'.format(str(self.loan_id), str(self.user.user_id))
