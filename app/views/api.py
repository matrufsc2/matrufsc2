import json
from app.json_serializer import encoder
from flask.helpers import make_response

__author__ = 'fernando'


def serialize(result, status=200, headers=None):
    if headers is None:
        headers = {}
    headers.setdefault("Content-Type", "application/json")
    if not result and not isinstance(result, list):
        return "", 404, headers
    response = make_response(encoder.encode(result), status, headers)
    return response


def api_index():
    return "", 404