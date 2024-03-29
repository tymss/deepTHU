from django.urls import path
from . import views
from .back_thread import init_thread

init_thread()

urlpatterns = [
    path('api/v1/src/upload', views.src_upload_view),
    path('api/v1/dst/upload', views.dst_upload_view),
    path('api/v1/task/query', views.task_query_view),
    path('api/v1/task/result', views.task_result_view)
]