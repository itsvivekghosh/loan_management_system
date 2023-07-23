"""
URL configuration for backend_assignment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from user.views import RegisterUser
from loan.views import ApplyLoan
from payments.views import FetchTransactionView, PaymentsView




urlpatterns = [
    
    # Admin URL
    path('admin/', admin.site.urls),
    
    # User URLS
    path('api/register-user/', RegisterUser.as_view(), name="Register User API"),

    # Loan APIs
    path('api/apply-loan/', ApplyLoan.as_view(), name="Loan APIs"),

    ## Payment APIs
    path('api/make-payment/', PaymentsView.as_view(), name="Make Payment"),
    
    # Get Transaction by Loan ID API
    path('api/get-statement/', FetchTransactionView.as_view(), name="Get Statemnet")
    
]
