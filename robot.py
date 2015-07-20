import os
import time
from app.cache import clear_lru_cache
from app.robot.robot import Robot
from flask import Flask, request, got_request_exception
import rollbar
import rollbar.contrib.flask
import logging

__author__ = 'fernando'

IN_DEV = "dev" in os.environ.get("SERVER_SOFTWARE", "").lower()
CACHE_RESPONSE_KEY = "cached/response/%d/%s"

app = Flask(__name__)

if not IN_DEV:
    rollbar.init(
        'ba9bf3c858294e0882d57a243084e20d',
        'production',
        root=os.path.dirname(os.path.realpath(__file__)),
        allow_logging_basic_config=False,
        handler='gae'
    )

    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


logging = logging.getLogger("matrufsc2")


@app.route("/secret/update/", methods=["GET", "POST"])
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

@app.route("/secret/clear_cache/", methods=["GET", "POST"])
def clear_cache():
    clear_lru_cache()
    return "OK", 200, {}

if __name__ == "__main__":
    app.run()