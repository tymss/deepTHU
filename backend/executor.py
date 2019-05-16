import threading
import os
import subprocess
from .configs import TASK_PATH, DEEPFACE_PATH, MAX_TRAINING_TIME
from .models import Task
from .utils import check_and_makedirs


class ExecThread(threading.Thread):

    def __init__(self, task_id):
        threading.Thread.__init__(self)
        self.task_id = task_id

    def run(self):
        print('Executing task %s...' % self.task_id)
        task_path = TASK_PATH + self.task_id
        objs = Task.objects.filter(task_id=self.task_id)
        if len(objs) != 1:
            print('Error: To execute a task not in database')
            return
        obj = objs[0]
        # create needed dirs of task
        check_and_makedirs(task_path + '/src_pic')
        check_and_makedirs(task_path + '/dst_pic')
        check_and_makedirs(task_path + '/src_face')
        check_and_makedirs(task_path + '/dst_face')
        check_and_makedirs(task_path + '/model')
        check_and_makedirs(task_path + '/result_pic')
        try:
            with open(task_path + '/task.log', 'a') as log_file:

                # convert src video into pics
                dirs = os.listdir(task_path + '/src')
                src_file = task_path + '/src/' + dirs[0]
                p = subprocess.Popen(['ffmpeg', '-i', src_file, '-r', '25', task_path + '/src_pic/%d.png'],
                                     stderr=log_file, stdout=log_file)
                try:
                    if p.wait() != 0:
                        raise Exception('Return code not 0 when convert src video to pics.')
                except:
                    raise

                # convert dst video into pics:
                dirs = os.listdir(task_path + '/dst')
                dst_file = task_path + '/dst/' + dirs[0]
                p = subprocess.Popen(['ffmpeg', '-i', dst_file, '-r', '25', task_path + '/dst_pic/%d.png'],
                                     stderr=log_file, stdout=log_file)
                try:
                    if p.wait() != 0:
                        raise Exception('Return code not 0 when convert dst video to pics.')
                except:
                    raise

                # extract src
                p = subprocess.Popen(
                    ['python', DEEPFACE_PATH, 'extract', '-i', task_path + '/src_pic', '-o', task_path + '/src_face'],
                    stderr=log_file, stdout=log_file)
                try:
                    if p.wait() != 0:
                        raise Exception('Return code not 0 when extracting src_face.')
                except:
                    raise

                # extract dst
                p = subprocess.Popen(
                    ['python', DEEPFACE_PATH, 'extract', '-i', task_path + '/dst_pic', '-o', task_path + '/dst_face'],
                    stderr=log_file, stdout=log_file)
                try:
                    if p.wait() != 0:
                        raise Exception('Return code not 0 when extracting dst_face.')
                except:
                    raise

                # train
                p = subprocess.Popen(
                    ['python', DEEPFACE_PATH, 'train', '-A', task_path + '/src_face', '-B', task_path + '/dst_face',
                     '-m', task_path + '/model'], stderr=log_file, stdout=log_file)
                try:
                    if p.wait(MAX_TRAINING_TIME) != 0:
                        raise Exception('Return code not 0 when training.')
                except subprocess.TimeoutExpired:
                    pass
                except:
                    raise

                # convert
                p = subprocess.Popen(
                    ['python', DEEPFACE_PATH, 'convert', '-i', task_path + '/dst_pic', '-o', task_path + '/result_pic',
                     '-m', task_path + '/model'], stderr=log_file, stdout=log_file)
                try:
                    if p.wait() != 0:
                        raise Exception('Return code not 0 when converting.')
                except:
                    raise

                # convert result pics into video
                p = subprocess.Popen(
                    ['ffmpeg', '-r', '25', '-i', task_path + '/result_pic/%d.png', 'result.mp4']
                )
                try:
                    if p.wait() != 0:
                        raise Exception('Return code not 0 when converting result pics into video.')
                except:
                    raise
                obj.state = 'FINISHED'
                obj.save()
        except:
            obj.state = 'FAILED'
            obj.save()

