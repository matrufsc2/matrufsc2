import json
from app.api import plans
from app.views.api import serialize
from flask import request
__author__ = 'fernando'


def get_plans():
    result = plans.get_plans(request.args.to_dict())
    return serialize(result)


def create_plan():
    try:
        request_body = request.get_data(as_text=True)
        request_body = json.loads(request_body)
        result = plans.create_plan(request_body)
    except (ValueError, KeyError), e:
        print e
        result = None
    return serialize(result)


def update_plan(id_value):
    try:
        request_body = request.get_data(as_text=True)
        request_body = json.loads(request_body)
        result = plans.update_plan(id_value, request_body)
    except (ValueError, KeyError):
        result = None
    return serialize(result)


def get_plan(id_value):
    result = plans.get_plan(id_value)
    return serialize(result)