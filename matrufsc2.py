import json
from flask import Flask, request
import os
from werkzeug.contrib.cache import GAEMemcachedCache
from app import api
from app.json_serializer import JSONEncoder
from app.robot.robot import Robot

app = Flask(__name__)

cache = GAEMemcachedCache()

CACHE_TIMEOUT = 3600
CACHE_KEY = "view/%s"

IN_DEV = "dev" in os.environ.get("SERVER_SOFTWARE", "").lower() or os.environ.has_key("DEV")

@app.before_request
def return_cached():
    # if GET and POST not empty
    if not request.values:
        response = cache.get(CACHE_KEY%request.path)
        if response:
            return response

@app.after_request
def cache_response(response):
    if not request.values and "update" not in request.path:
        cache.set(CACHE_KEY%(request.path), response, CACHE_TIMEOUT)
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
    result = list(api.get_campi(request.args))
    return serialize(result)


@app.route("/api/campi/<int:idValue>/")
def getCampus(idValue):
    result = api.get_campus(idValue)
    return serialize(result)

@app.route("/api/semesters/")
def getSemesters():
    result = list(api.get_semesters(request.args))
    return serialize(result)


@app.route("/api/semesters/<int:idValue>/")
def getSemester(idValue):
    result = api.get_semester(idValue)
    return serialize(result)


@app.route("/api/disciplines/")
def getDisciplines():
    result = list(api.get_disciplines(request.args))
    return serialize(result)


@app.route("/api/disciplines/<int:idValue>/")
def getDiscipline(idValue):
    result = api.get_discipline(idValue)
    return serialize(result)

@app.route("/api/teams/")
def getTeams():
    result = list(api.get_teams(request.args))
    return serialize(result)


@app.route("/api/teams/<int:idValue>/")
def getTeam(idValue):
    result = api.get_team(idValue)
    return serialize(result)

@app.route("/api/update/")
def update():
    robot = Robot("http://127.0.0.1:5000/%s/")
    fut = robot.run()
    """ :type: google.appengine.ext.ndb.Future """
    return fut.get_result()
app.debug = IN_DEV

if __name__ == "__main__":
    app.run()
else:
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
