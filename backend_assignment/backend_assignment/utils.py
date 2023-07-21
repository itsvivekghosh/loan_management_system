from rest_framework.response import Response
from rest_framework import status


def get_success_response(response_message) -> Response:

    return Response({
            'status': 'success',
            'message': response_message
        }, 
        status=status.HTTP_200_OK
    )


def get_error_response(error_message) -> Response:

    return Response({
            'status': 'error',
            'message': error_message
        }, 
        status=status.HTTP_400_BAD_REQUEST
    )

def get_fields_error_message(serializer) -> Response:

    error_object = {}
    for field_name, field_errors in serializer.errors.items():
        error_object[field_name] = field_errors[0]

    return Response({
            "status": "error",
            "message": error_object
        }, 
        status=status.HTTP_400_BAD_REQUEST
    )