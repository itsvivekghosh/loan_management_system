from django.urls import path, include
from .views import PaymentsView, FetchTransactionView
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    
    # Payment APIs
    path('make-payment/', PaymentsView.as_view(), name="Payment APIs"),
    
    # Get Transaction by Loan ID API
    path('get-statement/', FetchTransactionView.as_view(), name="Get Statemnet")
]