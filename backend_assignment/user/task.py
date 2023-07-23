
from celery import shared_task
import csv
from .models import User

from backend_assignment.utils import get_success_response, get_error_response
import backend_assignment.constants as constant



# celery -A backend_assignment.celery worker --pool=solo -l INFO

@shared_task
def calculateCreditScore(aadhar_number):

    try:
        ## Opening the Transactions CSV File
        with open("backend_assignment/static/data.csv") as csv_file:

            reader = csv.reader(csv_file)

            # Ignoring the first row as it may contain the column names
            # reader = next(reader)

            total_balance = 0
            credit_score = constant.MIN_CREDIT_VALUE
            credit_cross_balance = 0
            debit_cross_balance = 0

            # Reading each or row line of csv file
            for row in reader:  
                
                user_aadhar_number = str(row[0])

                ## If the aadhar number matching with the user aadhar number
                if aadhar_number == user_aadhar_number:
                
                    transaction_type = row[2]
                    amount = int(row[3])

                    if amount != 0 :

                        if transaction_type == constant.DEBIT:
                            total_balance -= amount
                            debit_cross_balance += amount
                
                        elif transaction_type == constant.CREDIT:
                            total_balance += amount
                            credit_cross_balance += amount
                    else:
                        total_balance += 0

                    if credit_cross_balance > constant.CROSS_BALANCE_CHECK:
                        credit_score += (credit_cross_balance // constant.CROSS_BALANCE_CHECK) * constant.CREDIT_SCORE_POINTS_VARIABLE
                        credit_cross_balance = 0

                    if debit_cross_balance > constant.CROSS_BALANCE_CHECK:
                        credit_score -= (debit_cross_balance // constant.CROSS_BALANCE_CHECK) * constant.CREDIT_SCORE_POINTS_VARIABLE
                        debit_cross_balance = 0

            ## Checking if Calculated credis score is within the required range:
            # -> if the balance is above 10 Lakh then, set max = 900 Credid score
            # -> if the balance is below 1 Lakh then, set min = 300 Credit score   
            if (total_balance >= constant.MAX_BANK_BALANCE_CHECK or credit_score > constant.MAX_CREDIT_SCORE):
                credit_score = constant.MAX_CREDIT_SCORE
            elif (total_balance <= constant.MIN_BANK_BALANCE_CHECK or credit_score < constant.MIN_CREDIT_VALUE):
                credit_score = constant.MIN_CREDIT_VALUE
        
        User.objects.filter(
            aadhar_number = aadhar_number
        ).update(
            credit_score = credit_score
        )

        message = 'Total Balance for {} : {} & Credit Score is: {}'.format(aadhar_number, total_balance, credit_score)
        return get_success_response(message).data
    
    except Exception as e:
        message = 'Error while calculating the credit score, Error Cause: {}'.format(str(e))
        return get_error_response(message).data


'''
{
    "aadhar_number": "1051ed87-1007-4d3b-8d11-b02ab008e2ea",
    "name": "Vivek Ghosh",
    "email": "vivek@email.com",
    "annual_income": 500000
}

'''