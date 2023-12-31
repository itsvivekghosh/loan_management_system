from rest_framework import serializers
from .models import Payments


class PaymentSerializer(serializers.ModelSerializer):

	class Meta:
		model = Payments
		fields = (
			"payment_id",
            "loan_id",
            "payment_timestamp",
	    	'amount'
		)


class GetTransactionSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Payments
		fields = (
			'payment_id',
			'loan_id',
			"payment_timestamp",
		)