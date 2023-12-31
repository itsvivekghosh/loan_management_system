from user.models import User
from enum import Enum
import math
from datetime import datetime, timedelta
from calendar import monthrange

import backend_assignment.constants as constant 



class LOANTYPE(Enum):
    '''
    Loan Type ENUM
    '''
    CAR = constant.CAR
    PERSONAL = constant.PERSONAL
    EDUCATION = constant.EDUCATION
    HOME = constant.HOME


def validate_loan_requirements(user: User, data):
    '''
        Validation of all loan requirements and checking if the loan of the amount can be sanctioned or not.
    '''

    if user.credit_score < constant.MIN_CREDIT_SCORE:
        return get_response_data(False, "Your credit score is less then 450")
    
    if user.annual_income < constant.MIN_ANNUAL_INCOME:
        return get_response_data(False, "Your Annual Income is then {}".format(constant.MIN_ANNUAL_INCOME))
    
    amount, loan_type = data["loan_amount"], data["loan_type"]
    if loan_type == LOANTYPE.CAR.value and amount > constant.CAR_LOAN_MIN_AMOUNT:
        return get_response_data(False, "Loan amount for {} LOAN should be less then {}".format(LOANTYPE.CAR.value, constant.CAR_LOAN_MIN_AMOUNT))
    
    if loan_type == LOANTYPE.HOME.value and amount > constant.HOME_LOAN_MIN_AMOUNT:
        return get_response_data(False, "Loan amount for {} LOAN should be less then {}".format(LOANTYPE.HOME.value, constant.HOME_LOAN_MIN_AMOUNT))
    
    if loan_type == LOANTYPE.EDUCATION.value and amount > constant.EDUCATION_LOAN_MIN_AMOUNT:
        return get_response_data(False, "Loan amount for {} LOAN should be less then {}".format(LOANTYPE.EDUCATION.value, constant.EDUCATION_LOAN_MIN_AMOUNT))
    
    if loan_type == LOANTYPE.PERSONAL.value and amount > constant.PERSONAL_LOAN_MIN_AMOUNT:
        return get_response_data(False, "Loan amount for {} LOAN should be less then {}".format(LOANTYPE.PERSONAL.value, constant.PERSONAL_LOAN_MIN_AMOUNT))
    
    if data["interest_rate"] < constant.MIN_INTEREST_RATE:
        return get_response_data(False, "Interest Rate should not be less then {}".format(constant.MIN_INTEREST_RATE))
    
    emi_validation_obj = validate_emi_requirements(data, user)
    emi_status, emi_message = emi_validation_obj['status'], emi_validation_obj['message']
    if emi_status == False:
        return emi_validation_obj

    return get_response_data(True, emi_message)




def validate_emi_requirements(data, user):
    '''
    Validate all the calculated Loan EMI requirements
    '''
    
    emi_amount = calculate_emi(data)

    # EMI amount must be at-most 60% of the monthly income of the User
    user_monthly_income_per_emi = (((user.annual_income / 12) * 60) / 100)
    # print(user_monthly_income_per_emi, emi_amount)

    if emi_amount > user_monthly_income_per_emi:
        return get_response_data(False, """EMI amount should be less then 60 percent of the monthly income of the User!""")
    
    interest_earned = (emi_amount * data["term_period"] - data["loan_amount"])
    # # Total interest earned should be > 10000
    if interest_earned < constant.MIN_INTEREST_EARNING:
        return get_response_data(False, """EMI amount should be more then {}!""".format(constant.MIN_INTEREST_EARNING))

    
    return get_response_data(True, emi_amount)



def get_response_data(status, message):

    return {
        "status": status,
        'message': message 
    }





'''
This function calculates the Loan EMI
EMI = p * r * (1+r)^n/((1+r)^n-1)

Where:
p = Principal or Loan Amount
r = Interest Rate Per Month
n = Number of monthly installments

If the interest rate per annum is R% then interest rate per month is calculated using:
Monthly Interest Rate (r) = R/(12*100)
'''
def calculate_emi(data):
    
    PRINCIPAL_AMOUNT = data["loan_amount"]
    ANNUAL_INTEREST_RATE = data["interest_rate"]
    NO_OF_MONTHS = data["term_period"]

    # Calculating interest rate per month
    INTEREST_RATE = ANNUAL_INTEREST_RATE/(12*100)

    # Calculating Equated Monthly Installment (EMI)
    EMI_AMOUNT = PRINCIPAL_AMOUNT * INTEREST_RATE * ((1+INTEREST_RATE)**NO_OF_MONTHS)/((1+INTEREST_RATE)**NO_OF_MONTHS - 1)

    # EMI_AMOUNT = (PRINCIPAL_AMOUNT * INTEREST_RATE * pow(1 + INTEREST_RATE, NO_OF_MONTHS)) / (pow(1 + INTEREST_RATE, NO_OF_MONTHS) - 1)
    return math.ceil(EMI_AMOUNT)





def calculate_due_dates_with_amount(amount, loan_date, term_period, loan_amount, interest_rate):
    '''
    Calculate the Due dates and emi amount with the due dates and principal & interest amounts.
    Save in DB.
    '''
    listData = []
    loan_amount_ = loan_amount
    for index in range(term_period):
        
        dateTimeObj = datetime.strptime(loan_date, "%Y-%m-%d") # to datetime
        next_date = nextDateUtil(dateTimeObj).strftime("%Y-%m-%d")
        interest_on_emi = loan_amount_*(interest_rate/100) / 12
        principal_amount = amount - interest_on_emi
        loan_amount_ -= principal_amount

        if (loan_amount_ < 0):
            loan_amount_ = 0
        
        emi_date_object = {
            "emi_month_number": index+1,
            "due_date": next_date,
            "due_amount": amount,
            "emi_paid": False,
            "interest_on_emi": math.floor(interest_on_emi),
            'principal_amount': math.floor(principal_amount),
            'outstanding_balance': math.floor(loan_amount_)
        }
        listData.append(emi_date_object)
        loan_date = next_date
    
    return (listData)



def nextDate(today_date):
    '''
    Calculates the next day of current date
    '''
    year = today_date.year
    month = today_date.month
    
    days_in_month = monthrange(year, month)[1]
    next_month = today_date + timedelta(days=days_in_month)
    return next_month


def nextDateUtil(current_date:datetime):
    '''
    Calculates the next day of current date and also calculates the first day of due date of next month
    '''
    current_date = current_date.replace(day=1)
    current_date = current_date + timedelta(days=32)
    next_date = current_date.replace(day=1)

    return next_date



def get_loan_payment_due_dates_list(payment_list):
    '''
    Returns the loan payment due date list from payment list
    '''
    response = []
    for data in payment_list:
        res = {
            "due_date": data['due_date'],
            'emi_due_amount': data['due_amount']
        }
        response.append(res)
    return response