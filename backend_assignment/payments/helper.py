from loan.models import Loan
from datetime import datetime
from loan.helper import calculate_emi

from backend_assignment.utils import *
import math


def check_if_previous_emis_are_due(data, loan: Loan) -> Response:
    
    try:

        loan_emis_list = loan.emi_due_dates_with_payment_history
        current_date = datetime.now().date()

        for data in loan_emis_list:
            if current_date > datetime.strptime(data['due_date'], "%Y-%m-%d").date():
                # print('last month due date:', data['due_date'])
                if data['emi_paid'] == False:
                    return get_success_response('Pervious EMIs are not paid!')
                break

        return get_error_response('Previous EMIs are paid successfully')
    
    except Exception as e:
        message = 'Error while checking Previous EMIs are due or not, Error Cause'.format(str(e))
        return get_error_response(error_message=message)



def update_emi_list_for_payment_util_(request_data, loan: Loan) -> Response:

    try:

        is_any_payment_done = False
        updated_month_index = -1
        current_date = datetime.now().date()
        emi_amount, emi_new_amount = -1, 0
        loan_paid_month, new_emi_object = None, None

        if float(loan.emi_amount) != float(request_data['amount']):
            data = {
                'loan_amount': loan.loan_amount - request_data['amount'],
                'interest_rate': loan.interest_rate,
                'term_period': loan.term_period
            }
            new_emi_object = data

            ## Calculating the new EMI Amount
            emi_new_amount = math.ceil(loan.emi_amount + (loan.emi_amount - request_data['amount'])/data["term_period"])

        else:
            emi_amount = loan.emi_amount


        for data in loan.emi_due_dates_with_payment_history:
            
            due_date_time = datetime.strptime(data['due_date'], "%Y-%m-%d").date()

            if current_date <= due_date_time and is_any_payment_done == False:

                if data['emi_paid'] == False:
                    data["emi_paid"] = True
                    loan.total_loan_amount_paid += request_data['amount']
                    is_any_payment_done = True
                    updated_month_index = data['emi_month_number']
                    loan_paid_month = data['due_date']

                else:
                    return get_error_response("EMI is already paid for month!")

                # break

            elif request_data['amount'] != loan.emi_amount and current_date <= due_date_time:

                # Updating the EMID Due dates Loan Objects
                data['due_amount'] = emi_amount

                interest_on_emi = new_emi_object['loan_amount']*(loan.interest_rate/100) / 12
                principal_amount = emi_new_amount - interest_on_emi
                new_emi_object['loan_amount'] -= principal_amount

                if (new_emi_object['loan_amount'] < 0):
                    new_emi_object['loan_amount'] = 0
                
                data["due_amount"] = emi_new_amount
                data["interest_on_emi"] = math.ceil(interest_on_emi)
                data['principal_amount'] = math.ceil(principal_amount)
                data['outstanding_balance'] = math.ceil(new_emi_object['loan_amount'])
                

        if is_any_payment_done:
            loan.save()

        else:
            return get_error_response("Error while marking any payment, Please check all the previous EMIs are paid or not!")

        return get_success_response({
            "updated_month_index": updated_month_index,
            'loan_paid_month': loan_paid_month,
        })
    
    except Exception as e:
        message = 'Error while updating EMI list for Payment, Error Cause: {}'.format(str(e))
        return get_error_response(message)


def get_principal_amount_and_interest_amount(data_list, month_index):

    try:
        for data in data_list:
            if data['emi_month_number'] == month_index:
                return (data['principal_amount'], data['interest_on_emi'])

        return (None, None)
    
    except Exception as e:
        return (None, None) 
    
