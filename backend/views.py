from rest_framework.response import Response
from .serializer import get_err_response
from rest_framework.decorators import api_view
import uuid
from .models import Task

@api_view(['GET', 'POST', ])
def src_upload_view(request):

    if request.method == 'POST':
        task_id = uuid.uuid4()
        obj, is_created = Task.objects.get_or_create(task_id=task_id)
        while not is_created:
            task_id = uuid.uuid4()
            obj, is_created = Task.objects.get_or_create(task_id=task_id)
        print(task_id)
    else:
        return Response(get_err_response('Method Not Supported.'), status=400)

@api_view(['GET', 'POST', ])
def dst_upload_view(request):

    if request.method == 'POST':
        id = request.GET
        if id is None:
            return Response(get_err_response('Parameter \'task_id\' Needed.'), status=400)


    else:
        return Response(get_err_response('Method Not Supported.'), status=400)


@api_view(['GET', 'POST', ])
def task_query_view(request):

    return 0


@api_view(['GET', 'POST', ])
def task_result_view(request):

    return 0