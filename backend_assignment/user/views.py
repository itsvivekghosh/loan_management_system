
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .task import calculateCreditScore
from .models import *
from .serializers import UserSerializer


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
                aadhar_number = user_data["aadhar_number"],
                name=user_data["name"],
                email=user_data["email"],
                annual_income=user_data["annual_income"]
            )
            calculateCreditScore.delay(user_data["aadhar_number"])

            created_user = User.objects.get(
                aadhar_number=user_data["aadhar_number"]
            )
            
            response_data = {
                "status": "success",
                "message": {
                    "uuid": created_user.user_id,
                    "aadhar_number": created_user.aadhar_number
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