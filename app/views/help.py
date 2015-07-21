from app.api import help
from app.views.api import serialize
from flask import request

__author__ = 'fernando'


def get_sections():
    result = help.get_sections(request.args.to_dict())
    return serialize(result)


def get_section(id_value):
    result = help.get_section(id_value)
    return serialize(result)


def get_questions_groups():
    result = help.get_questions_groups(request.args.to_dict())
    return serialize(result)


def get_question_group(id_value):
    result = help.get_question_group(id_value)
    return serialize(result)


def get_articles():
    result = help.get_articles(request.args.to_dict())
    return serialize(result)


def get_article(id_value):
    result = help.get_article(id_value)
    return serialize(result)