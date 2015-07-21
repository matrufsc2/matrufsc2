from app.api import campi
from app.views.api import serialize
from flask import request

__author__ = 'fernando'


def get_campi():
    args = request.args.to_dict()
    args["_full"] = False
    result = campi.get_campi(args)
    if "X_APPENGINE_CITYLATLONG" in request.headers:
        lat, lon = map(float, request.headers["X_APPENGINE_CITYLATLONG"].split(",", 1))
        result = campi.sort_campi_by_distance({
            "campi": result,
            "lat": lat,
            "lon": lon
        })
    return serialize(result)


def get_campus(id_value):
    result = campi.get_campus(id_value)
    return serialize(result)
