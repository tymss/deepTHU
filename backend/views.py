import uuid
import os
from rest_framework.response import Response
from .serializer import get_err_response, get_task_id_response, get_task_state_response
from rest_framework.decorators import api_view
from django.http.response import FileResponse
from .models import Task
from .configs import TASK_PATH, MAX_SIZE, SUPPORTED_FORMAT, MAX_TRAINING_HOURS
from .utils import check_and_makedirs, validate_email, send_mail


@api_view(['GET', 'POST', ])
def src_upload_view(request):
    if request.method == 'POST':
        ''' To get a unique uuid that not exists in the db. '''

        training_time = request.GET.get('training_time')
        email = request.GET.get('email')
        if training_time is None:
            return Response(get_err_response('Parameter \'training_time\' is needed.'), status=400)
        try:
            training_time = int(training_time)
        except:
            return Response(get_err_response('Training_time should be integer.'), status=400)
        if training_time > MAX_TRAINING_HOURS or training_time <= 0:
            return Response(get_err_response('Training_time should be less than %d and be more than 0.' % MAX_TRAINING_HOURS), status=400)
        if email is not None:
            if not validate_email(email):
                return Response(get_err_response('Wrong email format.'), status=400)

        task_id = str(uuid.uuid4())
        objs = Task.objects.filter(task_id=task_id)
        while len(objs) != 0:
            task_id = str(uuid.uuid4())
            objs = Task.objects.filter(task_id=task_id)

        files = request.FILES.getlist('file')
        if len(files) != 1:
            return Response(get_err_response('Only one file in field \'file\' should be uploaded.'), status=400)
        uploaded = files[0]
        if uploaded.size > MAX_SIZE:
            return Response(get_err_response('Your file should be smaller than %dB.' % MAX_SIZE), status=413)

        if uploaded.name.split('.')[-1] not in SUPPORTED_FORMAT:
            return Response(get_err_response('Video format not supported.'), status=400)

        if email is None:
            task = Task(task_id=task_id, training_time=training_time)
        else:
            task = Task(task_id=task_id, training_time=training_time, email=email)
        task.save()

        # makedir of task
        check_and_makedirs(TASK_PATH + task_id + '/src')

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

        if uploaded.name.split('.')[-1] not in SUPPORTED_FORMAT:
            return Response(get_err_response('Video format not supported.'), status=400)

        obj.dst_format = uploaded.name.split('.')[-1]

        file_path = task_path + '/dst/' + uploaded.name
        try:
            with open(file_path, 'wb') as f:
                for chunk in uploaded.chunks():
                    f.write(chunk)
        except Exception as e:  # error when saving
            if os.path.exists(file_path):
                os.remove(path=file_path)
            return Response(get_err_response('File cannot be saved because of some unknown reasons'), status=500)

        obj.state = 'CREATED'
        obj.save()

        if obj.email:
            send_mail(task_id, obj.email, 'CREATED')

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
            return FileResponse(open(result_file, 'rb'), as_attachment=True, filename=dirs[0])
        except Exception as e:
            return Response(get_err_response('Result cannot be downloaded because of unknown reasons.'), status=500)
    else:
        return Response(get_err_response('Method %s not supported.' % request.method), status=405)



