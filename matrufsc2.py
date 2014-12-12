import json
from flask import Flask, request, g
import os
from google.appengine.api import memcache
from app import api
from app.json_serializer import JSONEncoder
from app.robot.robot import Robot
import hashlib, logging
import cloudstorage as gcs
from google.appengine.api import app_identity

try:
    import cPickle as pickle
except ImportError:
    import pickle

app = Flask(__name__)

logging = logging.getLogger("matrufsc2")

CACHE_TIMEOUT = 600
CACHE_KEY = "view/%s"

IN_DEV = "dev" in os.environ.get("SERVER_SOFTWARE", "").lower() or os.environ.has_key("DEV")


def get_filename(filename):
    bucket_name = app_identity.get_default_gcs_bucket_name()
    bucket = "/" + bucket_name
    return "/".join([bucket, filename])


retry = gcs.RetryParams(initial_delay=0.2,
                        max_delay=2.0,
                        backoff_factor=2,
                        max_retry_period=15,
                        urlfetch_timeout=60)

gcs.set_default_retry_params(retry)


@app.before_request
def return_cached():
    if "update" not in request.path:
        url_hash = hashlib.sha1(request.url).hexdigest()
        response = memcache.get(CACHE_KEY % url_hash)
        if response:
            logging.debug("Found item on memcached..Returning")
            g.ignoreMiddleware = True
            return response
        filename = get_filename("cache/%s.json" % url_hash)
        try:
            gcs_file = gcs.open(filename, 'r')
            response = pickle.loads(gcs_file.read())
            gcs_file.close()
            logging.debug("Found item on GCS..Returning")
            try:
                logging.debug("Saving item on memcached..")
                memcache.set(CACHE_KEY % hashlib.sha1(request.url).hexdigest(), response, CACHE_TIMEOUT)
            except:
                pass
            g.ignoreMiddleware = True
            return response
        except:
            pass
        g.ignoreMiddleware = False


@app.after_request
def cache_response(response):
    if g.get("ignoreMiddleware"):
        return response
    response.headers["Cache-Control"] = "public, max-age=600"
    response.headers["Pragma"] = "cache"
    if "update" not in request.path:
        url_hash = hashlib.sha1(request.url).hexdigest()
        try:
            logging.debug("Saving item on memcached..")
            memcache.set(CACHE_KEY % url_hash, response, CACHE_TIMEOUT)
        except:
            pass
        try:
            filename = get_filename("cache/%s.json" % url_hash)
            gcs_file = gcs.open(filename, 'w', content_type="application/json")
            gcs_file.write(pickle.dumps(response))
            logging.debug("Saving item on GCS..")
            gcs_file.close()
        except:
            pass
    return response


@app.route("/api/")
def index():
    return "", 404


def serialize(result):
    if not result and not isinstance(result, list):
        return "", 404, {"Content-Type": "application/json"}
    return json.dumps(result, cls=JSONEncoder), 200, {"Content-Type": "application/json"}

@app.route("/api/semesters/")
def get_semesters():
    result = list(api.get_semesters(dict(request.args)))
    return serialize(result)


@app.route("/api/semesters/<idValue>/")
def get_semester(idValue):
    result = api.get_semester(idValue)
    return serialize(result)


@app.route("/api/campi/")
def get_campi():
    result = list(api.get_campi(dict(request.args)))
    return serialize(result)


@app.route("/api/campi/<idValue>/")
def get_campus(idValue):
    result = api.get_campus(idValue)
    return serialize(result)


@app.route("/api/disciplines/")
def get_disciplines():
    result = list(api.get_disciplines(dict(request.args)))
    return serialize(result)


@app.route("/api/disciplines/<idValue>/")
def get_discipline(idValue):
    result = api.get_discipline(idValue)
    return serialize(result)


@app.route("/api/teams/")
def get_teams():
    result = list(api.get_teams(dict(request.args)))
    return serialize(result)


@app.route("/api/teams/<idValue>/")
def get_team(idValue):
    result = api.get_team(idValue)
    return serialize(result)


@app.route("/secret/update/", methods=["GET", "POST"])
def update():
    robot = Robot("http://127.0.0.1:5000/%s/")
    fut = robot.run(request.get_data())
    """ :type: google.appengine.ext.ndb.Future """
    return fut.get_result()


app.debug = IN_DEV

if __name__ == "__main__":
    app.run()
else:
    from google.appengine.ext.appstats import recording

    app = recording.appstats_wsgi_middleware(app)
