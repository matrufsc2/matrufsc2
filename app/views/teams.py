from app.api import teams
from app.views.api import serialize
from flask import request

__author__ = 'fernando'


def get_teams():
    result = teams.get_teams(request.args.to_dict())
    return serialize(result)


def get_team(id_value):
    result = teams.get_team(id_value)
    return serialize(result)