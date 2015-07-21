from app.api import semesters
from app.views.api import serialize
from flask import request
__author__ = 'fernando'


def get_semesters():
    result = semesters.get_semesters(request.args.to_dict())
    return serialize(result)


def get_semester(id_value):
    result = semesters.get_semester(id_value)
    return serialize(result)