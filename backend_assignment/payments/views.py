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
from backend_assignment.utils import *
import backend_assignment.constants as constant

class PaymentsView(APIView):
    '''
    Payments View
    '''
    def get(self, request):
        '''
            Getting all the Payments as a list
        '''

        try:
            
            payments = Payments.objects.all().values()
            serializer = PaymentSerializer(payments, many=True)

            return Response(serializer.data)
        except Exception as e:
            message = 'Error while fetching the Statement List, Error Cause: {}'.format(str(e))
            return get_error_response(message)
    

    def post(self, request):
        '''
        Creating a payment by checking the requirements
        '''
        try:

            serializer = PaymentSerializer(data=request.data)

            if serializer.is_valid():
                
                ## Checking for Payment Requirements are correct or not
                loan = Loan.objects.get(loan_id = request.data["loan_id"])
                is_loan_payment_requirements_correct = self.check_loan_emi_payment_requirements_are_matching_(
                    request=request, loan=loan
                )

                ## Checking if the requiremenmts are correct
                if is_loan_payment_requirements_correct.data['status'] == constant.SUCCESS:
                    
                    ## updating the emi list for the month
                    updated_emi_list_response = update_emi_list_for_payment_util_(
                        request_data=request.data, 
                        loan=loan
                    )

                    if updated_emi_list_response.data['status'] == constant.SUCCESS:
                        
                        ## Creasting a payment request
                        return self.create_payment_response_(
                            request=request, 
                            loan=loan, 
                            updated_emi_list_response=updated_emi_list_response.data['message']
                        )
                        
                    else:
                        return updated_emi_list_response
                
                else:  
                    return is_loan_payment_requirements_correct
              
            return get_fields_error_message(serializer=serializer)
        
        ## Catching the exception and return error response
        except Exception as e:
            message = 'Error while making the payment, Error Cause: {}'.format(str(e))
            return get_error_response(message) 
        
        
    def check_loan_emi_payment_requirements_are_matching_(self, request, loan):
        '''
        Checking the payment of loan month requirements
        '''
        try:
            # Checking if the user has already paid for the current date or not
            # if yes, then rejecting the payment
            payments_of_todays_date = Payments.objects.filter(
                payment_timestamp = datetime(datetime.now(tz=timezone.utc).year, datetime.now().month, datetime.now().day)
            ).values()

            if len(payments_of_todays_date) > 0:
                return get_error_response("EMI Due already paid for today!")
            
            ## Check if the prev EMIs are due or not
            previous_emi_due = check_if_previous_emis_are_due(data=request.data, loan=loan)
            if previous_emi_due.data['status'] == constant.SUCCESS:
                return get_error_response("EMI Due Amount is not paid for last month!")
            
            return get_success_response('Payment Requirements Cleared!')
        
        except Exception as e:
            message = 'Error while checking Payment Requirements, Error Cause: {}'.format(str(e))
            return get_error_response(message)
        

    def create_payment_response_(self, request, loan, updated_emi_list_response) -> Response:
        '''
            Creating the payment response 
        '''
        try:

            principal_amount, interest_amount_paid = get_principal_amount_and_interest_amount(
                loan.emi_due_dates_with_payment_history, 
                updated_emi_list_response['updated_month_index']
            )

            ## Saving the Payment object
            payment = Payments.objects.create(
                amount = request.data['amount'],
                loan = loan,
                loan_paid_for_month_number = updated_emi_list_response['updated_month_index'],
                interest_paid = interest_amount_paid,
                principal_amount = principal_amount,
                loan_paid_month = updated_emi_list_response['loan_paid_month']
            )

            return get_success_response({
                'loan_id': payment.loan.loan_id,
                'payment_transaction_id': payment.payment_id,
                'amount_paid': payment.amount,
                'payment_timestamp': payment.payment_timestamp,
                'loan_paid_month': payment.loan_paid_month,
            })

        except Exception as e:
            message = 'Error while creating Payment Response, Error Cause: {}'.format(str(e))
            return get_error_response(message)


'''
{
    "loan_id": "",
    "amount": 10000
}

'''

class FetchTransactionView(APIView):

    def get(self, request):
        '''
        Getting all the transactions / statement list
        '''
        try:

            loan_id = request.headers['loan-id']
            payment_list = self.get_transactions_statement(loan_id=loan_id)
            return payment_list
        
        except Exception as e:
            message = ("Error while fetching details for Loan. Please check the Loan ID again.")
            return get_error_response(message)
        

    def get_transactions_statement(self, loan_id):
        '''
            Getting transactions list with past transaction and upcoming transactions
        '''
        try:

            transaction_list = Payments.objects.all().filter(loan_id=loan_id).values()
            loan_object = Loan.objects.get(loan_id=loan_id)

            past_transactions_response = self.get_past_transactions_response(transaction_list)
            upcoming_transactions = self.get_upcoming_transactions(loan_object)

            return self.create_transactions_statement_response(
                past_transactions_response,
                upcoming_transactions
            )
        
        except Exception as e:
            message = ("Error while fetching loan details for Loan ID: {}, Error Cause: {}".format(loan_id, str(e)))
            return get_error_response(message)
        

    def get_past_transactions_response(self, transaction_list):
        '''
        Getting all Past transactions
        '''
        try:

            past_transactions = []

            for data in transaction_list:

                past_transaction_object = {
                    'transaction_datetime': data['payment_timestamp'],
                    'principal_amount': data['principal_amount'],
                    'interest_paid': data['interest_paid'],
                    'amount_paid': data['amount'],
                    'month_paid': data['loan_paid_month']
                }
                past_transactions.append(past_transaction_object)

            return get_success_response(past_transactions)
        
        except Exception as e:
            message = ("Error while iterating in the transaction_list, Error Cause: {}".format(str(e)))
            return get_error_response(message)
    

    def get_upcoming_transactions(self, loan: Loan):
        '''
        Getting all upcoming transactions
        '''
        upcoming_payments = []

        try:

            for data in loan.emi_due_dates_with_payment_history:

                if data['emi_paid'] == False:
                    emi_payment_data = {
                        'emi_due_date': data['due_date'],
                        'amount_due': data['due_amount']
                    }
                    upcoming_payments.append(emi_payment_data)

            return get_success_response(upcoming_payments)
        
        except Exception as e:
            message = ("Error while iterating in the payment_list, Error Cause: {}".format(str(e)))
            return get_error_response(message)
        

    def create_transactions_statement_response(self, past_transactions_response: Response, upcoming_transactions: Response):
        '''
        Create the transaction statement response
        '''
        response = {}

        try:

            if past_transactions_response.data['status'] == constant.SUCCESS:
                response['past_transactions'] = past_transactions_response.data['message']

            if upcoming_transactions.data['status'] == constant.SUCCESS:
                response['upcoming_transactions'] = upcoming_transactions.data['message']

            return get_success_response(response_message=response)
        
        except Exception as e:
            message = 'Error while creating response object, Error Cause: {}'.format(str(e))
            return get_error_response(message)