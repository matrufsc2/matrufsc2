from app.api import pages
from app.views.api import serialize
from flask import request

__author__ = 'fernando'


def get_pages():
    result = pages.get_pages(request.args.to_dict())
    return serialize(result)


def get_page(slug):
    result = pages.get_page(slug)
    return serialize(result)