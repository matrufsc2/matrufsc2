import math

__author__ = 'fernando'


def distance_on_unit_sphere(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)