from rest_framework import status
from rest_framework.exceptions import APIException


class BraccioStatusNotOkException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'This braccio is not in a good status and thus cannot run routines'
    default_code = 'braccio_status_not_ok'


class BraccioBusyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'This braccio is busy running another routine.'
    default_code = 'braccio_busy'
