import json
from flask import Flask, request, g, got_request_exception
import os
import re
import urllib2
from google.appengine.api import memcache
from app import api
from app.json_serializer import JSONEncoder
from app.robot.robot import Robot
import hashlib, logging
import cloudstorage as gcs
from google.appengine.api import app_identity
import rollbar
import rollbar.contrib.flask

try:
    import cPickle as pickle
except ImportError:
    import pickle

app = Flask(__name__)

bots_re = re.compile("(baiduspider|twitterbot|facebookexternalhit|rogerbot|linkedinbot|embedly|quora link preview|showyoubot|outbrain|pinterest|slackbot)", re.IGNORECASE)
prerender_re = re.compile("Prerender", re.IGNORECASE)

IN_DEV = "dev" in os.environ.get("SERVER_SOFTWARE", "").lower()

if not IN_DEV:
    rollbar.init(
        'ba9bf3c858294e0882d57a243084e20d',
        'production',
        root=os.path.dirname(os.path.realpath(__file__)),
        allow_logging_basic_config=False
    )

    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

logging = logging.getLogger("matrufsc2")

CACHE_TIMEOUT = 600
CACHE_KEY = "view/%d/%s"


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

def can_prerender():
    prerender = False
    if request.args.has_key("_escaped_fragment_"):
        prerender = True
    user_agent = request.user_agent.string
    if bots_re.search(user_agent):
        prerender = True
    if prerender_re.search(user_agent):
        prerender = False
    print prerender
    return prerender

@app.before_request
def return_cached():
    if "update" not in request.path:
        prerender = can_prerender()
        url_hash = hashlib.sha1(request.url).hexdigest()
        cache_key = CACHE_KEY % (int(prerender), url_hash)
        response = memcache.get(cache_key)
        if response:
            logging.debug("Found item on memcached..Returning")
            g.ignoreMiddleware = True
            return response
        filename = get_filename(cache_key)
        try:
            gcs_file = gcs.open(filename, 'r')
            response = pickle.loads(gcs_file.read())
            gcs_file.close()
            logging.debug("Found item on GCS..Returning")
            try:
                logging.debug("Saving item on memcached..")
                memcache.set(cache_key, response, CACHE_TIMEOUT)
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
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["Pragma"] = "cache"
    if "update" not in request.path:
        prerender = can_prerender()
        url_hash = hashlib.sha1(request.url).hexdigest()
        cache_key = CACHE_KEY % (int(prerender), url_hash)
        try:
            logging.debug("Saving item on memcached..")
            memcache.set(cache_key, response, CACHE_TIMEOUT)
        except:
            pass
        try:
            filename = get_filename(cache_key)
            gcs_file = gcs.open(filename, 'w', content_type="application/json")
            gcs_file.write(pickle.dumps(response))
            logging.debug("Saving item on GCS..")
            gcs_file.close()
        except:
            pass
    return response


@app.route("/api/")
def api_index():
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
    if IN_DEV:
        robot_url = "http://127.0.0.1:5000/%s/"
    else:
        robot_url = "http://matrufsc2.fjorgemota.com/%s/"
    robot = Robot(robot_url)
    fut = robot.run(request.get_data())
    """ :type: google.appengine.ext.ndb.Future """
    return fut.get_result()

@app.route("/")
@app.route("/sobre/")
def index():
    prerender = can_prerender()
    if prerender:
        if IN_DEV:
            prerender_url = "http://127.0.0.1:3000/%s" % request.url
            handler_request = urllib2.Request(prerender_url)
        else:
            prerender_url = "http://service.prerender.io/%s" % request.url
            handler_request = urllib2.Request(prerender_url, headers={"X-Prerender-Token": "{{prerender_token}}"})
        handler = urllib2.urlopen(handler_request)
        content = handler.read()
        handler.close()
    else:
        if IN_DEV:
            prerender_filename = "frontend/views/index.html"
        else:
            prerender_filename = "frontend/views/index-optimize.html"
        arq = open(prerender_filename)
        content = arq.read()
        arq.close()
    return content, 200, {"Content-Type": "text/html; charset=UTF-8"}


app.debug = IN_DEV

if __name__ == "__main__":
    app.run()
else:
    from google.appengine.ext.appstats import recording

    app = recording.appstats_wsgi_middleware(app)
