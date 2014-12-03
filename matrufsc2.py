import json
from flask import Flask, request
import os
from google.appengine.api import memcache
from app import api
from app.json_serializer import JSONEncoder
from app.robot.robot import Robot
import hashlib

app = Flask(__name__)


CACHE_TIMEOUT = 3600
CACHE_KEY = "view/%s"

IN_DEV = "dev" in os.environ.get("SERVER_SOFTWARE", "").lower() or os.environ.has_key("DEV")

@app.before_request
def return_cached():
    if "update" not in request.path:
        response = memcache.get(CACHE_KEY%hashlib.sha1(request.url).hexdigest())
        if response:
            return response

@app.after_request
def cae_response(response):
    if "update" not in request.path:
        memcache.set(CACHE_KEY % hashlib.sha1(request.url).hexdigest(), response)
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["Pragma"] = "cache"
    return response

@app.route("/api/")
def index():
    return "", 404

def serialize(result):
    if not result and not isinstance(result, list):
        return "", 404, {"Content-Type": "application/json"}
    return json.dumps(result, cls=JSONEncoder), 200, {"Content-Type": "application/json"}


@app.route("/api/campi/")
def getCampi():
    result = list(api.get_campi(dict(request.args)))
    return serialize(result)


@app.route("/api/campi/<idValue>/")
def getCampus(idValue):
    result = api.get_campus(idValue)
    return serialize(result)

@app.route("/api/semesters/")
def getSemesters():
    result = list(api.get_semesters(dict(request.args)))
    return serialize(result)


@app.route("/api/semesters/<idValue>/")
def getSemester(idValue):
    result = api.get_semester(idValue)
    return serialize(result)


@app.route("/api/disciplines/")
def getDisciplines():
    result = list(api.get_disciplines(dict(request.args)))
    return serialize(result)


@app.route("/api/disciplines/<idValue>/")
def getDiscipline(idValue):
    result = api.get_discipline(idValue)
    return serialize(result)

@app.route("/api/teams/")
def getTeams():
    result = list(api.get_teams(dict(request.args)))
    return serialize(result)


@app.route("/api/teams/<idValue>/")
def getTeam(idValue):
    result = api.get_team(idValue)
    return serialize(result)

@app.route("/secret/update/", methods=["GET", "POST"])
def update():
    robot = Robot("http://matrufsc2.fjorgemota.com/%s/")
    fut = robot.run(request.get_data())
    """ :type: google.appengine.ext.ndb.Future """
    return fut.get_result()
app.debug = IN_DEV

if __name__ == "__main__":
    app.run()
else:
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
