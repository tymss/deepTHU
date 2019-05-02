from rest_framework.response import Response
from .serializer import get_err_response
from rest_framework.decorators import api_view

@api_view(['GET', 'POST', ])
def src_upload_view(request):

    if request.method == 'POST':
        return 0
    else:
        return Response(get_err_response('Method Not Supported.'), status=400)


def dst_upload_view(request):

    return 0

def task_query_view(request):

    return 0

def task_result_view(request):

    return 0