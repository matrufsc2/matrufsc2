import json
import urllib
from flask import Flask, request, g, got_request_exception
import os
import re
import urllib2
from google.appengine.api import memcache
from google.appengine.api.urlfetch import fetch
import zlib
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
        logging.debug("Pre-rendering because of _escaped_fragment_ parameter")
        prerender = True
    user_agent = request.user_agent.string
    if bots_re.search(user_agent):
        logging.debug("Pre-rendering because of user-agent")
        prerender = True
    if prerender_re.search(user_agent):
        logging.debug("Disabling Pre-rendering because of user-agent")
        prerender = False
    return prerender

@app.before_request
def return_cached():
    if request.method == "GET":
        prerender = can_prerender() and "/api/" not in request.base_url
        url_hash = hashlib.sha1(request.url).hexdigest()
        cache_key = CACHE_KEY % (int(prerender), url_hash)
        response = memcache.get(cache_key)
        if response:
            logging.debug("Found item on memcached..Returning")
            try:
                response = pickle.loads(zlib.decompress(response))
            except:
                pass
            g.ignoreMiddleware = True
            return response
        filename = get_filename(cache_key)
        try:
            gcs_file = gcs.open(filename, 'r')
            content = gcs_file.read()
            try:
                response = pickle.loads(zlib.decompress(content))
            except:
                response = pickle.loads(content)
            gcs_file.close()
            logging.debug("Found item on GCS..Returning")
            compressed_response = zlib.compress(pickle.dumps(response))
            try:
                logging.debug("Saving item on memcached..")
                memcache.set(cache_key, compressed_response, CACHE_TIMEOUT)
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
    if request.method == "GET":
        response.headers["Cache-Control"] = "public, max-age=3600"
        response.headers["Pragma"] = "cache"
        prerender = can_prerender() and "/api/" not in request.base_url
        url_hash = hashlib.sha1(request.url).hexdigest()
        cache_key = CACHE_KEY % (int(prerender), url_hash)
        compressed_response = zlib.compress(pickle.dumps(response))
        try:
            logging.debug("Saving item on memcached..")
            memcache.set(cache_key, compressed_response, CACHE_TIMEOUT)
        except:
            pass
        try:
            filename = get_filename(cache_key)
            gcs_file = gcs.open(filename, 'w', content_type="application/json")
            gcs_file.write(compressed_response)
            logging.debug("Saving item on GCS..")
            gcs_file.close()
        except:
            pass
    else:
        response.headers["Cache-Control"] = "private"
        response.headers["Pragma"] = "no-cache"

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

@app.route("/api/short/", methods=["POST"])
def short():
    args = request.form
    statusSessionKeys = [
        "semester",
        "campus",
        "discipline",
        "selectedDisciplines",
        "disabledTeams",
        "selectedCombination"
    ]
    num = 0
    for key in statusSessionKeys:
        if args.has_key(key):
            num += 1
    if num >= 2:
        host = app_identity.get_default_version_hostname()
        if "127.0.0.1" in host:
            return "{}", 406, {"Content-Type": "application/json"}
        content = {
            "longUrl": "http://%s/?%s"%(host, urllib.urlencode(args))
        }
        content = json.dumps(content)
        googl_api_key = "{{googl_api_key}}"
        if "googl_api_key" not in googl_api_key:
            googl_api_key = "?key=%s" % googl_api_key
        else:
            googl_api_key = ""
        req = urllib2.Request(
            "https://www.googleapis.com/urlshortener/v1/url%s"%googl_api_key,
            content,
            {
                "Content-Type": "application/json"
            }
        )
        handler = urllib2.urlopen(req)
        content = handler.read()
        content = json.loads(content)
        short_url = content["id"]
        return serialize({
            "shortUrl": short_url
        })
    else:
        return "{}", 406, {"Content-Type": "application/json"}

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
            prerender_headers = {}
        else:
            prerender_url = "http://service.prerender.io/%s" % request.url
            prerender_headers= {"X-Prerender-Token": "{{prerender_token}}"}
        try:
            logging.debug("Fetching prerender...")
            handler = fetch(prerender_url, headers=prerender_headers, allow_truncated=False,
                            deadline=60, follow_redirects=False)
            content = handler.content
            logging.debug("Prerender returned %d bytes...", len(content))
        except:
            prerender = False
    if not prerender:
        if IN_DEV:
            filename = "frontend/views/index.html"
        else:
            filename = "frontend/views/index-optimize.html"
        arq = open(filename)
        content = arq.read()
        arq.close()
        logging.debug("Reading %d bytes from HTML file", len(content))
    logging.debug("Sending %d bytes", len(content))
    return content, 200, {"Content-Type": "text/html; charset=UTF-8"}


app.debug = IN_DEV

if __name__ == "__main__":
    app.run()
else:
    from google.appengine.ext.appstats import recording

    app = recording.appstats_wsgi_middleware(app)
