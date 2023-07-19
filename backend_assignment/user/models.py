from django.db import models
import uuid

class User(models.Model):

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_aadhar_number = models.CharField(max_length=100, unique=True)
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    user_annual_income = models.BigIntegerField()
    user_credit_score = models.IntegerField(default=None, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.user_aadhar_number)
    
    def __getitem__(self):
        return User