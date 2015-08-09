import time
from app.cache import clear_lru_cache
from app.robot.robot import Robot
from flask import request
import logging as _logging
__author__ = 'fernando'

logging = _logging.getLogger("matrufsc2_secret")
logging.setLevel(_logging.DEBUG)

logging.debug("Loaded secret functions")


def update():
    logging.debug("Updating...")
    start = time.time()
    robot = Robot()
    fut = robot.run(request.get_data())
    """ :type: google.appengine.ext.ndb.Future """
    result = fut.get_result()
    if fut.get_traceback():
        print fut.get_traceback()
    logging.debug("Updated one page in %f seconds", time.time()-start)
    return result


def clear_cache():
    clear_lru_cache()
    return "OK", 200, {}
