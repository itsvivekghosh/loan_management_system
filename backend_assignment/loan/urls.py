from django.urls import path
from . import views

urlpatterns = [
    path("apply-loan/", view=views.ApplyLoan.as_view(), name="Apply Loan API")
]