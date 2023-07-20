
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import *
from .models import Loan
from .helper import validate_loan_requirements, calculate_due_dates_with_amount
from user.models import User



class ApplyLoan(APIView):

    def get(self, request):

        loans = Loan.objects.all().values()
        serializer = LoanSerializer(loans, many=True)

        return Response(serializer.data)
    
    def post(self, request):

        try:

            serializer = LoanSerializer(data=request.data)

            if serializer.is_valid():
                
                user = User.objects.get(
                    user_id = request.data["user_id"]
                )

                loan_check = validate_loan_requirements(user, request.data)
                loan_check_status, loan_check_message = loan_check["status"], loan_check["message"]

                if loan_check_status == True:

                    payment_due_dates_list = calculate_due_dates_with_amount(
                        loan_check_message, 
                        request.data['disbursement_date'], 
                        request.data['term_period']
                    )
                    total_loan_amount_with_interest = loan_check_message * request.data["term_period"]

                    created_loan_object = Loan.objects.create(
                        user = user,
                        loan_type = request.data["loan_type"],
                        loan_amount = request.data["loan_amount"],
                        interest_rate = request.data["interest_rate"],
                        term_period = request.data["term_period"],
                        disbursement_date = request.data["disbursement_date"],
                        emi_amount = loan_check_message,
                        total_loan_amount_with_interest = total_loan_amount_with_interest,
                        emi_due_dates_with_payment_history = payment_due_dates_list
                    )

                    response_data = {
                        "status": "success",
                        "message": {
                            'loan_id': created_loan_object.loan_id,
                            'total_loan_amount_with_interest': total_loan_amount_with_interest,
                            'due_dates': payment_due_dates_list,
                        }
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
                
                else:
                    response_data = {
                        "status": "error",
                        "message": loan_check_message
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            default_errors = serializer.errors
            new_error = {}
            for field_name, field_errors in default_errors.items():
                new_error[field_name] = field_errors[0]
            response_data = {
                "status": "error",
                "message": new_error
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            
            response_data = {
                "status": "error",
                "message": str(e)
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

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