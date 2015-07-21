import re, logging as _logging
from google.appengine.api.urlfetch import fetch
from flask import request
import os
__author__ = 'fernando'

IN_DEV = "dev" in os.environ.get("SERVER_SOFTWARE", "").lower()
bots_re = re.compile("(baiduspider|twitterbot|facebookexternalhit|rogerbot|linkedinbot|embedly|quora link preview|showyoubot|outbrain|pinterest|slackbot)", re.IGNORECASE)
prerender_re = re.compile("Prerender", re.IGNORECASE)
logging = _logging.getLogger("matrufsc2_other_pages")
logging.setLevel(_logging.DEBUG)

logging.debug("Loaded other pages")

def can_pre_render():
    pre_render = False
    if "_escaped_fragment_" in request.args:
        logging.debug("Pre-rendering because of _escaped_fragment_ parameter")
        pre_render = True
    user_agent = request.user_agent.string
    if bots_re.search(user_agent):
        logging.debug("Pre-rendering because of user-agent")
        pre_render = True
    if prerender_re.search(user_agent):
        logging.debug("Disabling Pre-rendering because of user-agent")
        pre_render = False
    return pre_render


def page(path):
    pre_render = can_pre_render()
    if pre_render:
        if IN_DEV:
            pre_render_url = "http://127.0.0.1:3000/%s" % request.url
            pre_render_headers = {}
        else:
            pre_render_url = "http://service.prerender.io/%s" % request.url
            pre_render_headers = {"X-Prerender-Token": "{{prerender_token}}"}
        try:
            handler = fetch(pre_render_url, headers=pre_render_headers, allow_truncated=False,
                            deadline=60, follow_redirects=False)
            content = handler.content
        except:
            pre_render = False
    if not pre_render:
        if IN_DEV:
            filename = "frontend/views/index.html"
        else:
            filename = "frontend/views/index-optimize.html"
        arq = open(filename)
        content = arq.read()
        if "io.prismic.preview" in request.cookies:
            content = content.replace(
                "{{prismicjs}}",
                "<script type=\"text/javascript\" src=\"//static.cdn.prismic.io/prismic.min.js\"></script>"
            )
        else:
            content = content.replace("{{prismicjs}}", "")
        arq.close()

    return content, 200, {"Content-Type": "text/html; charset=UTF-8"}

def index():
    return page("")