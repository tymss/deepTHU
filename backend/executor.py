import threading
import os
from .configs import TASK_PATH
from .models import Task


class ExecThread(threading.Thread):

    def __init__(self, task_id):
        threading.Thread.__init__(self)
        self.task_id = task_id

    def run(self):
        print('Executing task %s...' % self.task_id)
        path = TASK_PATH + self.task_id
        if not os.path.exists(path + '/src') or not os.path.exists(path + '/dst'):
            obj = Task.objects.get(task_id=self.task_id)
            obj.state = 'FAILED'
            obj.save()
            return
        # TODO: run this task
