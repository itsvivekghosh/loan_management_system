from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import PaymentSerializer
from payments.models import Payments
from loan.models import Loan
from datetime import datetime
from django.utils import timezone
from .helper import *

class PaymentsView(APIView):

    def get(self, request):

        return Response("Payment GET")
    

    def post(self, request):

        try:
            serializer = PaymentSerializer(data=request.data)

            loan = Loan.objects.get(
                loan_id = request.data["loan_id"]
            )

            # Checking if the user has already paid for the current date or not
            # if yes, then rejecting the payment
            payments_of_todays_date = Payments.objects.filter(
                payment_timestamp = datetime(datetime.now(tz=timezone.utc).year, datetime.now().month, datetime.now().day)
            ).values()

            if len(payments_of_todays_date) > 0:
                return Response(
                    {'status': "error", 'message': "EMI Due already paid for today!"},
                    status.HTTP_400_BAD_REQUEST
                )
            
            ## Check if the prev EMIs are due or not
            previous_emi_due = check_if_previous_emis_are_due(data=request.data, loan=loan)

            if previous_emi_due:
                return Response(
                    {'status': "error", 'message': "EMI Due Amount is not paid for last month!"},
                    status.HTTP_400_BAD_REQUEST
                )

            if serializer.is_valid():
                
                updated_emi_list_response = update_emi_list_for_payment_util(
                    request_data=request.data, 
                    loan=loan
                )

                if updated_emi_list_response['status'] == True:

                    Payments.objects.create(
                        amount = request.data['amount'],
                        loan = loan,
                        loan_paid_for_month_number = updated_emi_list_response['updated_month_index']
                    )

                    return Response({
                            'status': "success", 
                            'message': {
                                'loan_id': request.data["loan_id"],
                            }
                        },
                        status.HTTP_200_OK
                    )
                else:
                    return Response({
                        "status": "success",
                        "message": updated_emi_list_response['message']
                    })

        except Exception as e:
            return Response(
                {'status': "error", 'message': str(e)},
                status.HTTP_404_NOT_FOUND
            )


'''
{
    "loan_id": "",
    "amount": 10000
}

'''