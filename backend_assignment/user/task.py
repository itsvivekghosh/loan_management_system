
from celery import shared_task
import time, csv
from .models import User

import backend_assignment.constants as constant



# celery -A backend_assignment.celery worker --pool=solo -l INFO

@shared_task
def calculateCreditScore(aadhar_number):

    with open("backend_assignment/static/data.csv") as csv_file:

        reader = csv.reader(csv_file)
        total_balance = 0
        credit_score = constant.MIN_CREDIT_VALUE
        credit_cross_balance = 0
        debit_cross_balance = 0

        for row in reader:  
            
            user_aadhar_number = str(row[0])

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
            
        if (total_balance >= constant.MAX_BANK_BALANCE_CHECK or credit_score > constant.MAX_CREDIT_SCORE):
            credit_score = constant.MAX_CREDIT_SCORE
        elif (total_balance <= constant.MIN_BANK_BALANCE_CHECK or credit_score < constant.MIN_CREDIT_VALUE):
            credit_score = constant.MIN_CREDIT_VALUE
    
    # time.sleep(10)
    User.objects.filter(
        aadhar_number = aadhar_number
    ).update(
        credit_score = credit_score
    )

    return str('Total Balance for {} : {} & Credit Score is: {}'.format(aadhar_number, total_balance, credit_score))


'''
{
    "aadhar_number": "1051ed87-1007-4d3b-8d11-b02ab008e2ea",
    "name": "Vivek Ghosh",
    "email": "vivek@email.com",
    "annual_income": 500000
}

'''