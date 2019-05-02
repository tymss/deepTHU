from rest_framework.response import Response
from .serializer import get_err_response, get_task_id_response, get_task_state_response
from rest_framework.decorators import api_view
import uuid
from .models import Task


@api_view(['GET', 'POST', ])
def src_upload_view(request):
    if request.method == 'POST':
        ''' To get a unique uuid that not exists in the db. '''
        task_id = uuid.uuid4()
        obj, is_created = Task.objects.get_or_create(task_id=task_id)
        while not is_created:
            task_id = uuid.uuid4()
            obj, is_created = Task.objects.get_or_create(task_id=task_id)

        # TODO: upload file

    else:
        return Response(get_err_response('method %s is not supported.' % request.method), status=400)


@api_view(['GET', 'POST', ])
def dst_upload_view(request):
    if request.method == 'POST':
        id = request.GET.get('task_id')
        if id is None:
            return Response(get_err_response('parameter \'task_id\' is needed.'), status=400)
        try:
            obj = Task.objects.get(task_id=id)
        except Task.DoesNotExist:
            return Response(get_err_response('task:%s is not found.' % id), status=404)

        # TODO: upload file

        obj.state = 'CREATED'
        obj.save()
        return Response(get_task_id_response(id), status=200)

    else:
        return Response(get_err_response('method %s not supported.' % request.method), status=400)


@api_view(['GET', 'POST', ])
def task_query_view(request):
    if request.method == 'GET':
        id = request.GET.get('task_id')
        if id is None:
            return Response(get_err_response('parameter \'task_id\' is needed.'), status=400)
        try:
            obj = Task.objects.get(task_id=id)
        except Task.DoesNotExist:
            return Response(get_err_response('task:%s is not found.' % id), status=404)
        return Response(get_task_state_response(id, obj.state), status=200)

    else:
        return Response(get_err_response('method %s not supported.' % request.method), status=400)


@api_view(['GET', 'POST', ])
def task_result_view(request):
    if request.method == 'GET':
        id = request.GET.get('task_id')
        if id is None:
            return Response(get_err_response('parameter \'task_id\' is needed.'), status=400)
        try:
            obj = Task.objects.get(task_id=id)
        except Task.DoesNotExist:
            return Response(get_err_response('task:%s is not found.' % id), status=404)
        if obj.state != 'FINISHED':
            return Response(get_err_response('task:%s is not finished.' % id), status=409)
        # TODO: download file


    else:
        return Response(get_err_response('method %s not supported.' % request.method), status=400)
