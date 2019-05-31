import os
import shutil
import re


def check_and_makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)
        os.makedirs(path)


def validate_email(addr):
    if len(addr) > 7:
        if re.match('^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$', addr) is not None:
            return True
    return False

