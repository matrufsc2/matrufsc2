import json
from flask import Flask, request
import os
from werkzeug.contrib.cache import GAEMemcachedCache
from app import api
from app.services import Robot
from app.json_serializer import JSONEncoder

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
    if not request.values:
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
    result = list(api.getCampi(request.args))
    return serialize(result)


@app.route("/api/campi/<int:idValue>/")
def getCampus(idValue):
    result = api.getCampus(idValue)
    return serialize(result)

@app.route("/api/semesters/")
def getSemesters():
    result = list(api.getSemesters(request.args))
    return serialize(result)


@app.route("/api/semesters/<int:idValue>/")
def getSemester(idValue):
    result = api.getSemester(idValue)
    return serialize(result)


@app.route("/api/disciplines/")
def getDisciplines():
    result = list(api.getDisciplines(request.args))
    return serialize(result)


@app.route("/api/disciplines/<int:idValue>/")
def getDiscipline(idValue):
    result = api.getDiscipline(idValue)
    return serialize(result)

@app.route("/api/teams/")
def getTeams():
    result = list(api.getTeams(request.args))
    return serialize(result)


@app.route("/api/teams/<int:idValue>/")
def getTeam(idValue):
    result = api.getTeam(idValue)
    return serialize(result)

@app.route("/api/update")
def update():
    robot = Robot()
    fut = robot.run()
    exc = fut.get_exception()
    if exc:
        return str(exc),500
    else:
        return "OK", 200

app.debug = IN_DEV

if __name__ == "__main__":
    app.run()
else:
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
