from rest_framework import serializers


class ErrorData(object):
    def __init__(self, err_info):
        self.error_info = err_info


class ErrSerializer(serializers.Serializer):
    error_info = serializers.CharField(max_length=50)


class TaskIdData(object):
    def __init__(self, task_id):
        self.task_id = task_id


class TaskIdSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=32)


def get_err_response(err_info):
    err = ErrorData(err_info)
    serializer = ErrSerializer(err)
    return serializer.data


def get_task_id_response(taskid):
    task = TaskIdData(task_id=taskid)
    serializer = TaskIdSerializer(task)
    return serializer.data