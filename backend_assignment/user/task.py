
from celery import shared_task
import time, csv
from .models import User


# celery -A backend_assignment.celery worker --pool=solo -l INFO

@shared_task
def calculateCreditScore(aadhar_number):

    with open("backend_assignment/static/data.csv") as csv_file:

        reader = csv.reader(csv_file)
        total_balance = 0
        credit_score = 300
        credit_cross_balance = 0
        debit_cross_balance = 0

        for row in reader:  
            
            user_aadhar_number = str(row[0])

            if aadhar_number == user_aadhar_number:
            
                transaction_type = row[2]
                amount = int(row[3])

                if amount != 0 :

                    if transaction_type == 'DEBIT':
                        total_balance -= amount
                        debit_cross_balance += amount
            
                    elif transaction_type == "CREDIT":
                        total_balance += amount
                        credit_cross_balance += amount
                else:
                    total_balance += 0

                if credit_cross_balance > 15000:
                    credit_score += (credit_cross_balance // 15000) * 10
                    credit_cross_balance = 0

                if debit_cross_balance > 15000:
                    credit_score -= (debit_cross_balance // 15000) * 10
                    debit_cross_balance = 0
            
        if (total_balance >= 1000000 or credit_score > 900):
            credit_score = 900
        elif (total_balance <= 100000 or credit_score < 300):
            credit_score = 300
    
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