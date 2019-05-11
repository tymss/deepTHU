import threading
import time


class BackThread(threading.Thread):
    def run(self):
        print('Start backend thread...')
        # TODO: scan the database and make RUNNING into CREATED
        # TODO: while True: dispatch


def init_thread():
    thread = BackThread()
    thread.start()
