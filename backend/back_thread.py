import threading
import time
import os
import shutil
import pytz
from .models import Task
from datetime import datetime, timedelta
from .configs import TASK_MAX_DAYS, TASK_PATH, REFRESH_INTERVAL, MAX_RUNNING_NUM, TEMP_PATH
from .executor import ExecThread
from .utils import check_and_makedirs


class BackThread(threading.Thread):

    def run(self):
        print('Starting backend thread...')
        ite = 0
        if not os.path.exists(TASK_PATH + 'log'):
            os.makedirs(TASK_PATH + 'log')
        while True:
            """ clean overtime tasks """
            time_limit = datetime.now(tz=pytz.UTC) - timedelta(days=TASK_MAX_DAYS)
            objs = Task.objects.filter(create_time__lte=time_limit)
            for each in objs:
                if each.state != 'RUNNING':
                    path = TASK_PATH + each.task_id
                    if os.path.exists(path):
                        shutil.rmtree(path)
                    path = TEMP_PATH + each.task_id
                    if os.path.exists(path):
                        shutil.rmtree(path)
                    each.delete()

            """ clean failed tasks """
            objs = Task.objects.filter(state='FAILED')
            for each in objs:
                path = TASK_PATH + each.task_id
                if os.path.exists(path):
                    shutil.rmtree(path)
                path = TEMP_PATH + each.task_id
                if os.path.exists(path):
                    shutil.rmtree(path)

            """ clean finished tasks' temp """
            objs = Task.objects.filter(state='FINISHED')
            for each in objs:
                path = TEMP_PATH + each.task_id
                if os.path.exists(path):
                    shutil.rmtree(path)

            """ schedule """
            objs = Task.objects.filter(state='RUNNING')
            running_num = len(objs)
            while running_num < MAX_RUNNING_NUM:
                waiting = Task.objects.filter(state='CREATED').order_by('create_time')
                if len(waiting) > 0:
                    to_run = waiting[0]
                    to_run.state = 'RUNNING'
                    to_run.save()
                    exe_thread = ExecThread(to_run.task_id)
                    exe_thread.start()
                    running_num += 1
                else:
                    break
            ite += 1
            time.sleep(REFRESH_INTERVAL)


def init_thread():
    """ add all RUNNING (not finished) tasks into waiting list. """
    running_objs = Task.objects.filter(state='RUNNING')
    for each in running_objs:
        task_path = TASK_PATH + each.task_id
        temp_path = TEMP_PATH + each.task_id
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        if os.path.exists(task_path + '/sound'):
            shutil.rmtree(task_path + '/sound')
        if os.path.exists(task_path + '/model'):
            shutil.rmtree(task_path + '/model')
        if os.path.exists(task_path + '/result'):
            shutil.rmtree(task_path + '/result')
        each.state = 'CREATED'
        each.save()
    thread = BackThread()
    thread.start()

