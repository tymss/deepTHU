from rest_framework import serializers


'''
Serializers to convert classes into json objects.
You can use these serializers by calling functions like: get_xxx_response
instead of using these classes directly.
'''
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

class TaskStateData(object):
    def __init__(self, taskid, state, position):
        self.task_id = taskid
        self.task_state = state
        self.waiting_position = position

class TaskStateSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=32)
    task_state = serializers.CharField(max_length=20)
    waiting_position = serializers.IntegerField()


def get_err_response(err_info):
    err = ErrorData(err_info)
    serializer = ErrSerializer(err)
    return serializer.data


def get_task_id_response(taskid):
    task = TaskIdData(task_id=taskid)
    serializer = TaskIdSerializer(task)
    return serializer.data


def get_task_state_response(id, state, position):
    ts = TaskStateData(id, state, position)
    serializer = TaskStateSerializer(ts)
    return serializer.data