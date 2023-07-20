from django.urls import path, include
from .views import PaymentsView


urlpatterns = [
    
    # Payment APIs
    path('make-payment/', PaymentsView.as_view(), name="Payment APIs"),
    
]