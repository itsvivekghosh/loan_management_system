from django.shortcuts import render
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import PaymentSerializer, GetTransactionSerializer
from payments.models import Payments
from loan.models import Loan
from .helper import *

from datetime import datetime



class PaymentsView(APIView):

    def get(self, request):

        payments = Payments.objects.all().values()
        serializer = PaymentSerializer(payments, many=True)

        return Response(serializer.data)
    

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

                    principal_amount, interest_amount_paid = get_principal_amount_and_interest_amount(loan.emi_due_dates_with_payment_history, updated_emi_list_response['updated_month_index'])
                    
                    payment = Payments.objects.create(
                        amount = request.data['amount'],
                        loan = loan,
                        loan_paid_for_month_number = updated_emi_list_response['updated_month_index'],
                        interest_paid = interest_amount_paid,
                        principal_amount = principal_amount,
                        loan_paid_month = updated_emi_list_response['loan_paid_month']
                    )

                    return Response({
                            'status': "success", 
                            'message': {
                                'loan_id': request.data["loan_id"],
                                'payment_transaction_id': payment.payment_id,
                                'amount_paid': payment.amount,
                                'payment_timestamp': payment.payment_timestamp,
                                'loan_paid_month': payment.loan_paid_month
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

class FetchTransactionView(APIView):

    def get(self, request, format=None):
        try:
            loan_id = request.headers['loan-id']
            try:
                
                payment_list = self.get_transactions_statement(loan_id=loan_id)
                return payment_list
            
            except Exception as e:
                message = ("Error while fetching details for Loan ID: {}. Please check the Loan ID again.".format(loan_id))
                return Response({
                    'status': 'error',
                    "message": message
                }, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            message = "Invalid API Request, cause: {}".format(e)
            return Response({
                'status': 'error',
                "message": message
            }, status.HTTP_400_BAD_REQUEST)
        

    def get_transactions_statement(self, loan_id):
        try:

            transaction_list = Payments.objects.all().filter(loan_id=loan_id).values()
            loan_object = Loan.objects.get(loan_id=loan_id)

            past_transactions_response = self.get_past_transactions_response(transaction_list)
            upcoming_transactions = self.get_upcoming_transactions(loan_object)

            response = {
                'past_transactions': past_transactions_response,
                'upcoming_transactions': upcoming_transactions
            }
            return Response({
                'status': 'success',
                "message": response
            }, status.HTTP_200_OK)
        
        except Exception as e:
            message = ("Error while fetching loan details for Loan ID: {}".format(loan_id))
            return Response({
                'status': 'error',
                "message": message
            }, status.HTTP_404_NOT_FOUND)
        

    def get_past_transactions_response(self, transaction_list):

        response = []

        for data in transaction_list:
            ans = {
                'transaction_datetime': data['payment_timestamp'],
                'principal_amount': data['principal_amount'],
                'interest_paid': data['interest_paid'],
                'amount_paid': data['amount'],
            }
            response.append(ans)

        return response
    

    def get_upcoming_transactions(self, loan: Loan):
        
        payment_list = loan.emi_due_dates_with_payment_history
        upcoming_payments = []

        for data in payment_list:

            if data['emi_paid'] == False:
                emi_payment_data = {
                    'emi_due_date': data['due_date'],
                    'amount_due': data['due_amount']
                }
                upcoming_payments.append(emi_payment_data)

        return upcoming_payments