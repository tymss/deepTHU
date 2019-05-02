from rest_framework import serializers


class ErrorData(object):
    def __init__(self, err_info):
        self.error_info = err_info

class ErrSerializer(serializers.Serializer):
    error_info = serializers.CharField(max_length=50)

def get_err_response(err_info):
    err = ErrorData(err_info)
    serializer = ErrSerializer(err)
    return serializer.data