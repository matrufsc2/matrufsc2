from app.api import blog
from app.views.api import serialize
from flask import request
__author__ = 'fernando'


def get_categories():
    result = blog.get_categories(request.args.to_dict())
    return serialize(result)


def get_category(id_value):
    result = blog.get_category(id_value)
    return serialize(result)


def get_posts():
    result = blog.get_posts(request.args.to_dict())
    return serialize(result)


def get_post(id_value):
    result = blog.get_post(id_value)
    return serialize(result)


def get_blog_feed(type):
    type = type.lower()
    if type not in ["rss", "atom"]:
        return "", 404
    return blog.get_feed(type == 'atom'), 200, {"Content-Type": "application/rss+xml"}