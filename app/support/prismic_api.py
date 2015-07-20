from app import cache
import prismic
from google.appengine.ext import ndb
import rollbar
from app.support.domain import get_domain
from flask import request

__author__ = 'fernando'


def prismic_custom_request_handler(url):
    resp = ndb.get_context().urlfetch(url).get_result()
    return resp.status_code, resp.content, resp.headers


def prismic_link_resolver(doc):
    fmt = None
    if doc.type == "page":
        fmt = "/%s/%s/"
    elif doc.type == "question-group":
        fmt = "/ajuda/perguntas-frequentes/%s/%s/"
    elif doc.type == "post":
        fmt = "/blog/post/%s/%s/"
    elif doc.type == "category":
        fmt = "/blog/categoria/%s/%s/"
    elif doc.type == "section":
        fmt = "/ajuda/secao/%s/%s/"
    elif doc.type == "article":
        fmt = "/ajuda/artigo/%s/%s/"
    elif doc.type == "author":
        fmt = "/blog/autor/%s/%s/"
    if fmt is None:
        rollbar.report_message("Found link with unrecognized document type '%s'!" % doc.type, request=request)
        return "javascript:alert('Tipo de link nao reconhecido! Tente novamente mais tarde');"
    else:
        return fmt % (doc.slug, doc.id)


def prismic_full_link_resolver(doc):
    return "".join(["http://", get_domain(), prismic_link_resolver(doc)])


def prismic_html_serializer(block, content):
    return None


def get_prismic_api():
    return prismic.get(
        "http://matrufsc2.cdn.prismic.io/api",
        None,
        cache,
        prismic_custom_request_handler
    )


def get_prismic_form(ref=None, form="everything"):
    prismic_api = get_prismic_api()
    if ref is None:
        if "io.prismic.preview" in request.cookies:
            ref = request.cookies["io.prismic.preview"]
        else:
            ref = prismic_api.get_master()
    form = prismic_api.form(form)
    form.ref(ref)
    return form