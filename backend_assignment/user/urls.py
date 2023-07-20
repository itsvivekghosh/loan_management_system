from django.urls import path
from . import views

urlpatterns = [
    path("register-user/", view=views.RegisterUser.as_view(), name="User Register API")
]