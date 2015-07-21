from app.api import disciplines
from app.views.api import serialize
from flask import request

__author__ = 'fernando'


def get_disciplines():
    result = disciplines.get_disciplines(request.args.to_dict())
    return serialize(result)


def get_discipline(id_value):
    result = disciplines.get_discipline(id_value)
    return serialize(result)