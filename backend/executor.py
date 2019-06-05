import threading
import os
import subprocess
from .configs import TASK_PATH, DEEPFACE_PATH, TEMP_PATH, NORMAL_TASK_TIME_MAX
from .models import Task
from .utils import check_and_makedirs, send_mail


class ExecThread(threading.Thread):

    def __init__(self, task_id):
        threading.Thread.__init__(self)
        self.task_id = task_id

    def run(self):
        print('Executing task %s...' % self.task_id)
        task_path = TASK_PATH + self.task_id
        temp_path = TEMP_PATH + self.task_id
        objs = Task.objects.filter(task_id=self.task_id)
        if len(objs) != 1:
            print('Error: To execute a task not in database')
            return
        obj = objs[0]
        # create needed dirs of task
        check_and_makedirs(task_path + '/sound')
        check_and_makedirs(temp_path + '/src_pic')
        check_and_makedirs(temp_path + '/dst_pic')
        check_and_makedirs(temp_path + '/src_face')
        check_and_makedirs(temp_path + '/dst_face')
        check_and_makedirs(task_path + '/model')
        check_and_makedirs(temp_path + '/result_pic')
        check_and_makedirs(temp_path + '/no_sound')
        check_and_makedirs(task_path + '/result')
        try:
            with open(task_path + '/task.log', 'a') as log_file:

                # convert src video into pics
                dirs = os.listdir(task_path + '/src')
                src_file = task_path + '/src/' + dirs[0]
                p = subprocess.Popen(['ffmpeg', '-i', src_file, '-r', '30', temp_path + '/src_pic/%d.png'],
                                     stderr=log_file, stdout=log_file)
                try:
                    if p.wait(NORMAL_TASK_TIME_MAX) != 0:
                        raise Exception('Return code not 0 when convert src video to pics.')
                except:
                    raise

                # convert dst video into pics:
                dirs = os.listdir(task_path + '/dst')
                dst_file = task_path + '/dst/' + dirs[0]
                p = subprocess.Popen(['ffmpeg', '-i', dst_file, '-r', '30', temp_path + '/dst_pic/%d.png'],
                                     stderr=log_file, stdout=log_file)
                try:
                    if p.wait(NORMAL_TASK_TIME_MAX) != 0:
                        raise Exception('Return code not 0 when convert dst video to pics.')
                except:
                    raise

                # extract sound of video
                p = subprocess.Popen(['ffmpeg', '-i', dst_file, '-acodec', 'copy', '-vn',
                                      task_path + '/sound/audio.aac'], stderr=log_file, stdout=log_file)
                try:
                    if p.wait(NORMAL_TASK_TIME_MAX) != 0:
                        raise Exception('Return code not 0 when extract sound from dst.')
                except:
                    raise

                # extract src
                p = subprocess.Popen(
                    ['python', DEEPFACE_PATH, 'extract', '-i', temp_path + '/src_pic', '-o', temp_path + '/src_face'],
                    stderr=log_file, stdout=log_file)
                try:
                    if p.wait(NORMAL_TASK_TIME_MAX) != 0:
                        raise Exception('Return code not 0 when extracting src_face.')
                except:
                    raise

                # extract dst
                p = subprocess.Popen(
                    ['python', DEEPFACE_PATH, 'extract', '-i', temp_path + '/dst_pic', '-o', temp_path + '/dst_face'],
                    stderr=log_file, stdout=log_file)
                try:
                    if p.wait(NORMAL_TASK_TIME_MAX) != 0:
                        raise Exception('Return code not 0 when extracting dst_face.')
                except:
                    raise

                # train
                p = subprocess.Popen(
                    ['python', DEEPFACE_PATH, 'train', '-A', temp_path + '/dst_face', '-B', temp_path + '/src_face',
                     '-m', task_path + '/model'], stderr=log_file, stdout=log_file)
                try:
                    if p.wait(obj.training_time * 3600 - 1800) != 0:
                        raise Exception('Return code not 0 when training.')
                except subprocess.TimeoutExpired:
                    p.kill()
                except:
                    raise

                # convert
                p = subprocess.Popen(
                    ['python', DEEPFACE_PATH, 'convert', '-i', temp_path + '/dst_pic', '-o', temp_path + '/result_pic',
                     '-m', task_path + '/model'], stderr=log_file, stdout=log_file)
                try:
                    if p.wait(NORMAL_TASK_TIME_MAX) != 0:
                        raise Exception('Return code not 0 when converting.')
                except:
                    raise

                # convert result pics into video
                p = subprocess.Popen(
                    ['ffmpeg', '-r', '30', '-i', temp_path + '/result_pic/%d.png', '-pix_fmt', 'yuv420p', temp_path +
                     '/no_sound/result.' + obj.dst_format], stderr=log_file, stdout=log_file)
                try:
                    if p.wait(NORMAL_TASK_TIME_MAX) != 0:
                        raise Exception('Return code not 0 when converting result pics into video.')
                except:
                    raise

                # add sound to result
                p = subprocess.Popen(['ffmpeg', '-i', temp_path + '/no_sound/result.' + obj.dst_format, '-i',
                                      task_path + '/sound/audio.aac', task_path + '/result/result.' + obj.dst_format],
                                     stderr=log_file, stdout=log_file)
                try:
                    if p.wait(NORMAL_TASK_TIME_MAX) != 0:
                        raise Exception('Return code not 0 when add sound to result.')
                except:
                    raise

                obj.state = 'FINISHED'
                obj.save()
                if obj.email:
                    send_mail(self.task_id, obj.email, 'FINISHED')
        except Exception as e:
            print(e)
            obj.state = 'FAILED'
            obj.save()

