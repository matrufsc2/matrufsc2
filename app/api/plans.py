import calendar
import datetime
from google.appengine.ext import ndb
from app.models import Plan
from app.repositories import PlansRepository

__author__ = 'fernando'


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
    model.put(use_cache=False, use_memcache=True)
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
    model.put(use_cache=False, use_memcache=True)
    # Update cache too
    return model
