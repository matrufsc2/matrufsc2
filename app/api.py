import logging
import datetime, calendar
from google.appengine.ext import ndb
import math
from app.repositories import CampusRepository, DisciplinesRepository, TeamsRepository, SemesterRepository, \
    PlansRepository
from app.decorators import cacheable, searchable
from app.models import Plan
import operator

__author__ = 'fernando'

logging = logging.getLogger("matrufsc2_api")

# mapping with LAT/LONG for some of the cities
CAMPI_LAT_LON = {
    "CBS": [-27.282778, -50.583889],
    "ARA": [-28.935, -49.485833],
    "BLN": [-26.908889, -49.072222],
    "FLO": [-27.596944, -48.548889],
    "JOI": [-26.303889, -48.845833]
}


def distance_on_unit_sphere(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


def get_campi_key(campus, lat, lon):
    campus_lat_lon = CAMPI_LAT_LON.get(campus.name, [0, 0])
    return distance_on_unit_sphere(lat, lon, campus_lat_lon[0], campus_lat_lon[1])


def sort_campi_by_distance(filters):
    campi = filters["campi"]
    lat = filters["lat"]
    lon = filters["lon"]
    return map(
        operator.itemgetter(1),
        sorted(
            zip(
                map(
                    get_campi_key,
                    campi,
                    (lat for _ in campi),
                    (lon for _ in campi),
                ),
                campi
            ),
            key=operator.itemgetter(0)
        )
    )


@cacheable(consider_only=[])
def get_semesters(filters):
    repository = SemesterRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()

@cacheable()
def get_semester(id_value):
    repository = SemesterRepository()
    return repository.find_by_id(id_value).get_result()

@cacheable(consider_only=["semester"])
def get_campi(filters):
    repository = CampusRepository()
    if filters:
        campi = repository.find_by(filters).get_result()
    else:
        campi = repository.find_all().get_result()
    for campus in campi:
        campus.disciplines = []
    return campi

@cacheable()
def get_campus(id_value):
    repository = CampusRepository()
    campus = repository.find_by_id(id_value).get_result()
    campus.disciplines = []
    return campus

@searchable(
    lambda item: " - ".join([item['code'], item['name']]),
    prefix="matrufsc2-discipline-",
    consider_only=['campus']
)
def get_disciplines(filters):
    repository = DisciplinesRepository()
    if filters:
        disciplines = repository.find_by(filters).get_result()
    else:
        disciplines = repository.find_all().get_result()
    for discipline in disciplines:
        discipline.teams = []
    return disciplines


@cacheable()
def get_discipline(id_value):
    repository = DisciplinesRepository()
    discipline = repository.find_by_id(id_value).get_result()
    if discipline:
        discipline.teams = []
    return discipline

@cacheable(consider_only=["discipline"])
def get_teams(filters):
    repository = TeamsRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


@cacheable()
def get_team(id_value):
    repository = TeamsRepository()
    return repository.find_by_id(id_value).get_result()


def get_plan(plan_id):
    repository = PlansRepository()
    return repository.find_by_id(plan_id).get_result()


def get_plans(data):
    if "code" not in data:
        return []
    code = Plan.generate_id_string(data["code"])
    result = []
    match = get_plan(code)
    if match:
        result.append(match)
    return result


@ndb.transactional
def create_plan(data):
    if "code" not in data or "data" not in data:
        return False
    code = data["code"]
    plan_id = Plan.generate_id_string(code)
    if get_plan(plan_id): # Check in cache AND in database
        return False
    model = Plan(
        key=ndb.Key(Plan, plan_id),
        code=code,
        history=[{
            "id": calendar.timegm(datetime.datetime.now().utctimetuple()),
            "data": data["data"]
        }]
    )
    model.put()
    return model


@ndb.transactional
def update_plan(plan_id, data):
    if "code" not in data or "data" not in data:
        return False
    plan_id_test = Plan.generate_id_string(data["code"])
    if plan_id_test != plan_id:
        return False
    model = get_plan(plan_id) # Get from cache if available
    # Get the UTC timestamp
    now = calendar.timegm(datetime.datetime.now().utctimetuple())
    # Identify possible duplicates:
    while True:
        found = False
        for item in model.history:
            if item["id"] == now:
                now += 1
                found = True
        if not found:
            break
    model.history.insert(0, {
        "id": now,
        "data": data["data"]
    })
    # Hard limit to history: 10 itens
    if len(model.history) > 10:
        model.history.pop()
    model.put()
    # Update cache too
    return model
