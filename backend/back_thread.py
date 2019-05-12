import threading
import time
import os, shutil
import pytz
from .models import Task
from datetime import datetime, timedelta
from .configs import TASK_MAX_DAYS, TASK_PATH, REFRESH_INTERVAL


class BackThread(threading.Thread):

    def run(self):
        print('Start backend thread...')
        while True:
            """ clean overtime tasks """
            time_limit = datetime.now(tz=pytz.UTC) - timedelta(days=TASK_MAX_DAYS)
            objs = Task.objects.filter(create_time__lte=time_limit)
            for each in objs:
                if each.state != 'RUNNING':
                    path = TASK_PATH + each.task_id
                    if os.path.exists(path):
                        shutil.rmtree(path)
                    each.delete()

            """ dispatch """
            # TODO: dispatch
            time.sleep(REFRESH_INTERVAL)


def init_thread():
    """ add all RUNNING (not finished) tasks into waiting list. """
    running_objs = Task.objects.filter(state='RUNNING')
    for each in running_objs:
        each.state = 'CREATED'
        each.save()
    thread = BackThread()
    thread.start()

