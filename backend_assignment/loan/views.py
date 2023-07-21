
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import *
from .models import Loan
from .helper import validate_loan_requirements, calculate_due_dates_with_amount, get_loan_payment_due_dates_list
from user.models import User
from backend_assignment.utils import *



class ApplyLoan(APIView):

    def get(self, request):

        try:

            loans = Loan.objects.all().values()
            serializer = LoanSerializer(loans, many=True)

            return get_success_response(response_message=serializer.data)
        
        except Exception as e:
            message = "Error while getting the Loan list, Error Cause: {}".format(e)
            return get_error_response(error_message=message)

    
    def post(self, request):

        try:

            serializer = LoanSerializer(data=request.data)

            if serializer.is_valid():
                
                user = User.objects.get(user_id = request.data["user_id"])

                loan_check = validate_loan_requirements(user, request.data)
                loan_check_status, loan_check_message = loan_check["status"], loan_check["message"]

                if loan_check_status == True:

                    return self.create_loan_util(
                        request=request, 
                        user=user, 
                        loan_check_message=loan_check_message
                    )
                
                else:
                    return get_error_response(loan_check_message)

            return get_fields_error_message(serializer=serializer)
        
        except Exception as e:
            
            message = 'Error while Creating the Loan Object, Error Cause: {}'.format(str(e))
            return get_error_response(message)
        

    def create_loan_util(self, request, user, loan_check_message):

        try:

            payment_due_dates_list = calculate_due_dates_with_amount(
                loan_check_message, 
                request.data['disbursement_date'], 
                request.data['term_period'],
                request.data['loan_amount'],
                request.data['interest_rate']
            )

            total_loan_amount_with_interest = loan_check_message * request.data["term_period"]
            payment_due_dates_list_response = get_loan_payment_due_dates_list(payment_due_dates_list)

            return self.create_loan_object(
                request, 
                user, 
                total_loan_amount_with_interest, 
                loan_check_message, 
                payment_due_dates_list,
                payment_due_dates_list_response
            )
        
        except Exception as e:
            message = 'Error while creating Loan, Error Cause: {}'.format(str(e))
            return get_error_response(error_message=message)


    def create_loan_object(self, request, user, total_loan_amount_with_interest, loan_check_message, payment_due_dates_list, payment_due_dates_list_response):
        
        try:
            
            created_loan_object = Loan.objects.create(
                user = user,
                loan_type = request.data["loan_type"],
                loan_amount = request.data["loan_amount"],
                interest_rate = request.data["interest_rate"],
                interest_amount = total_loan_amount_with_interest - request.data['loan_amount'],
                term_period = request.data["term_period"],
                disbursement_date = request.data["disbursement_date"],
                emi_amount = loan_check_message,
                total_loan_amount_with_interest = total_loan_amount_with_interest,
                emi_due_dates_with_payment_history = payment_due_dates_list
            )

            return get_success_response({
                'loan_id': created_loan_object.loan_id,
                'total_loan_amount_with_interest': total_loan_amount_with_interest,
                'due_dates': payment_due_dates_list_response,
            })

        except Exception as e:
            message = 'Error while creating Loan, Cause: {}'.format(str(e))
            return get_error_response(error_message=message)
        

'''
{
    "user_id":"8742dc35a0a54bb68aae2d280a6d6f55",
    "loan_type": "Car",
    "loan_amount": 1000000,
    "interest_rate": 10,
    "term_period": 36,
    "disbursement_date": "2023-09-28"
}

'''