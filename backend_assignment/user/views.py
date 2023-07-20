
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .task import calculateCreditScore
from .models import *
from .serlializers import UserSerializer


class RegisterUser(APIView):
    
    def get(self, request):

        users = User.objects.all().values()
    
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    

    def post(self, request):

        user_data = request.data
        serializer = UserSerializer(data=user_data)

        if serializer.is_valid():
            
            User.objects.create(
                user_aadhar_number = user_data["user_aadhar_number"],
                user_name=user_data["user_name"],
                user_email=user_data["user_email"],
                user_annual_income=user_data["user_annual_income"]
            )
            calculateCreditScore.delay(user_data["user_aadhar_number"])

            created_user = User.objects.get(
                user_aadhar_number=user_data["user_aadhar_number"]
            )
            
            response_data = {
                "status": "success",
                "message": {
                    "user_uuid": created_user.user_id,
                    "user_aadhar_number": created_user.user_aadhar_number
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        default_errors = serializer.errors
        new_error = {}
        for field_name, field_errors in default_errors.items():
            new_error[field_name] = field_errors[0]
        response_data = {
            "status": "error",
            "message": new_error
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)