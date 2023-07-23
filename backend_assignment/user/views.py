
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .task import calculateCreditScore
from .models import *
from .serializers import UserSerializer
from backend_assignment.utils import get_error_response, get_success_response, get_fields_error_message



class RegisterUser(APIView):
    
    def get(self, request):
        '''
            Getting the list of all the Registered Users
        '''

        try:
            users = User.objects.all().values()
            serializer = UserSerializer(users, many=True)
            return get_success_response(serializer.data)
        
        except Exception as e:
            message = 'Error while getting the Users, Error Cause: {}'.format(e)
            return get_error_response(message)
    

    def post(self, request):
        '''
            Registering the user
        '''

        register_user_response = self.register_user(user_data=request.data)
        return register_user_response
        

    def register_user(self, user_data):
        '''
            Creating the user as per the aadhar number
        '''
        try:

            serializer = UserSerializer(data=user_data)

            if serializer.is_valid():

                created_user = User.objects.create(
                    aadhar_number = user_data["aadhar_number"],
                    name=user_data["name"],
                    email=user_data["email"],
                    annual_income=user_data["annual_income"]
                )

                calculateCreditScore.delay(user_data["aadhar_number"])

                return get_success_response({
                    "uuid": created_user.user_id,
                    "aadhar_number": created_user.aadhar_number
                })
            
            return get_fields_error_message(serializer=serializer)

        except Exception as e:
            message = 'Error while creating the User, Error Cause: {}'.format(e)
            return get_error_response(message)