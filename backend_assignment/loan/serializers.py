from rest_framework import serializers
from .models import Loan
from user.models import User


class LoanSerializer(serializers.ModelSerializer):

	class Meta:
		model = Loan
		fields = (
			'loan_id', 'user_id', 
			'loan_type', 'loan_amount', 
			'interest_rate',
			"term_period",
			"emi_amount",
			"disbursement_date",
		)