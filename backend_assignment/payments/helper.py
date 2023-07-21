from loan.models import Loan
from datetime import datetime
from loan.helper import calculate_emi

def check_if_previous_emis_are_due(data, loan: Loan):
    
    loan_emis_list = loan.emi_due_dates_with_payment_history
    current_date = datetime.now().date()

    for data in loan_emis_list:
        if current_date > datetime.strptime(data['due_date'], "%Y-%m-%d").date():
            # print('last month due date:', data['due_date'])
            if data['emi_paid'] == False:
                return True
            break

    return False


def update_emi_list_for_payment(data, loan: Loan):

    is_any_payment_done = False
    updated_month_index = -1
    current_date = datetime.now().date()

    for data in loan.emi_due_dates_with_payment_history:

        if current_date <= datetime.strptime(data['due_date'], "%Y-%m-%d").date():

            if data['emi_paid'] == False:
                # print('changing emi_paid value for ', data['due_date'], data['emi_month_number'])
                data["emi_paid"] = True
                is_any_payment_done = True
                updated_month_index = data['emi_month_number']

            else:
                return {
                    "status": False, 
                    "message": "EMI is already paid for month!"
                }

            break

    if is_any_payment_done:
        loan.save()
        # print('saving...')

    else:
        return {
            "status": False,
            "message": "Error while marking any payment, Please check all the previous EMIs are paid or not!"
        }

    return {
        "status": True, 
        "message": "EMI Paid successfully for this month!",
        "updated_month_index": updated_month_index
    } 



def update_emi_list_for_payment_util(request_data, loan: Loan):

    is_any_payment_done = False
    updated_month_index = -1
    current_date = datetime.now().date()
    emi_amount, diff_emi_new_amount = -1, 0

    if loan.emi_amount != request_data['amount']:
        data = {
            'loan_amount': loan.loan_amount - (loan.total_loan_amount_paid + abs(loan.emi_amount - request_data['amount'])),
            'interest_rate': loan.interest_rate,
            'term_period': loan.term_period
        }
        emi_amount = calculate_emi(data)
        diff_emi_new_amount = loan.emi_amount - emi_amount
    else:
        emi_amount = loan.emi_amount

    # print(loan.emi_amount, emi_amount, diff_emi_new_amount)


    for data in loan.emi_due_dates_with_payment_history:
        
        due_date_time = datetime.strptime(data['due_date'], "%Y-%m-%d").date()
        # print(current_date, due_date_time)
        if current_date <= due_date_time and is_any_payment_done == False:

            if data['emi_paid'] == False:
                data["emi_paid"] = True
                loan.total_loan_amount_paid += request_data['amount']
                is_any_payment_done = True
                updated_month_index = data['emi_month_number']

            else:
                return {
                    "status": False, 
                    "message": "EMI is already paid for month!"
                }

            # break

        elif request_data['amount'] != loan.emi_amount and current_date <= due_date_time:
            data['due_amount'] = emi_amount

    if is_any_payment_done:
        loan.save()
        # print('saving...')

    else:
        return {
            "status": False,
            "message": "Error while marking any payment, Please check all the previous EMIs are paid or not!"
        }

    return {
        "status": True, 
        "message": "EMI Paid successfully for this month!",
        "updated_month_index": updated_month_index
    } 


def get_principal_amount_and_interest_amount(data_list, month_index):

    for data in data_list:
        if data['emi_month_number'] == month_index:
            return (data['principal_amount'], data['interest_on_emi'])

    return (None, None)
