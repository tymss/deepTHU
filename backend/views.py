import uuid
import os
from rest_framework.response import Response
from .serializer import get_err_response, get_task_id_response, get_task_state_response
from rest_framework.decorators import api_view
from django.http.response import FileResponse
from .models import Task
from .configs import TASK_PATH, MAX_SIZE


@api_view(['GET', 'POST', ])
def src_upload_view(request):
    if request.method == 'POST':
        ''' To get a unique uuid that not exists in the db. '''

        task_id = str(uuid.uuid4())
        obj, is_created = Task.objects.get_or_create(task_id=task_id)
        while not is_created:
            task_id = str(uuid.uuid4())
            obj, is_created = Task.objects.get_or_create(task_id=task_id)

        # makedir of task
        check_and_makedirs(TASK_PATH + task_id + '/src')

        files = request.FILES.getlist('file')
        if len(files) != 1:
            return Response(get_err_response('Only one file in field \'file\' should be uploaded.'), status=400)
        uploaded = files[0]
        if uploaded.size > MAX_SIZE:
            return Response(get_err_response('Your file should be smaller than %dB.' % MAX_SIZE), status=413)

        # TODO: to check the type of uploaded file

        file_path = TASK_PATH + task_id + '/src/' + uploaded.name
        try:
            with open(file_path, 'wb') as f:
                for chunk in uploaded.chunks():
                    f.write(chunk)
        except Exception as e:  # error when saving
            if os.path.exists(file_path):
                os.remove(path=file_path)
            return Response(get_err_response('File cannot be saved because of some unknown reasons'), status=500)
        # success
        return Response(get_task_id_response(task_id), status=200)

    else:
        return Response(get_err_response('Method %s is not supported.' % request.method), status=405)


@api_view(['GET', 'POST', ])
def dst_upload_view(request):
    if request.method == 'POST':
        task_id = request.GET.get('task_id')
        if task_id is None:
            return Response(get_err_response('Parameter \'task_id\' is needed.'), status=400)
        try:
            obj = Task.objects.get(task_id=task_id)
        except Task.DoesNotExist:
            return Response(get_err_response('Task:%s is not found.' % task_id), status=404)
        if obj.state != 'CREATING':
            return Response(get_err_response('Task:%s is not creating.' % task_id), status=409)

        task_path = TASK_PATH + task_id

        check_and_makedirs(task_path + '/dst')

        files = request.FILES.getlist('file')
        if len(files) != 1:
            return Response(get_err_response('Only one file in field \'file\' should be uploaded.'), status=400)
        uploaded = files[0]
        if uploaded.size > MAX_SIZE:
            return Response(get_err_response('Your file should be smaller than %dB.' % MAX_SIZE), status=413)

        # TODO: to check the type of uploaded file

        file_path = task_path + '/dst/' + uploaded.name
        try:
            with open(file_path, 'wb') as f:
                for chunk in uploaded.chunks():
                    f.write(chunk)
        except Exception as e:  # error when saving
            if os.path.exists(file_path):
                os.remove(path=file_path)
            return Response(get_err_response('File cannot be saved because of some unknown reasons'), status=500)

        # create needed dirs of task
        check_and_makedirs(task_path + '/src_pic')
        check_and_makedirs(task_path + '/dst_pic')
        check_and_makedirs(task_path + '/src_face')
        check_and_makedirs(task_path + '/dst_face')
        check_and_makedirs(task_path + '/model')
        check_and_makedirs(task_path + '/result_pic')

        obj.state = 'CREATED'
        obj.save()
        return Response(get_task_id_response(task_id), status=200)

    else:
        return Response(get_err_response('Method %s not supported.' % request.method), status=405)


@api_view(['GET', 'POST', ])
def task_query_view(request):
    if request.method == 'GET':
        id = request.GET.get('task_id')
        if id is None:
            return Response(get_err_response('Parameter \'task_id\' is needed.'), status=400)
        try:
            obj = Task.objects.get(task_id=id)
        except Task.DoesNotExist:
            return Response(get_err_response('Task:%s is not found.' % id), status=404)
        return Response(get_task_state_response(id, obj.state), status=200)

    else:
        return Response(get_err_response('Method %s not supported.' % request.method), status=405)


@api_view(['GET', 'POST', ])
def task_result_view(request):
    if request.method == 'GET':
        task_id = request.GET.get('task_id')
        if task_id is None:
            return Response(get_err_response('Parameter \'task_id\' is needed.'), status=400)
        try:
            obj = Task.objects.get(task_id=task_id)
        except Task.DoesNotExist:
            return Response(get_err_response('Task:%s is not found.' % task_id), status=404)
        if obj.state != 'FINISHED':
            return Response(get_err_response('Task:%s is not finished.' % task_id), status=409)

        result_dir = TASK_PATH + task_id + '/result'
        try:
            dirs = os.listdir(result_dir)
            result_file = result_dir + '/' + dirs[0]
            return FileResponse(open(result_file, 'rb'), filename=dirs[0])
        except Exception as e:
            return Response(get_err_response('Result cannot be downloaded because of unknown reasons.'), status=500)
    else:
        return Response(get_err_response('Method %s not supported.' % request.method), status=405)


def check_and_makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
