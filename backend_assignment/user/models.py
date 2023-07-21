from django.db import models
import uuid

class User(models.Model):

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aadhar_number = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=75, unique=True)
    annual_income = models.BigIntegerField()
    credit_score = models.IntegerField(default=None, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.email)
    
    def __getitem__(self):
        return User
    
    class Meta:
        db_table = 'users'