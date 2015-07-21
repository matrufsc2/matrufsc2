from app.support.prismic_api import get_prismic_api, prismic_full_link_resolver
from flask import request
__author__ = 'fernando'


def prismic_preview():
    form = get_prismic_api()
    preview_token = request.args.to_dict().get("token")
    if not preview_token:
        return "", 404
    redirect_url = form.preview_session(preview_token, prismic_full_link_resolver(), "/")
    response = "", 302, {"Location": redirect_url}
    response.set_cookie("io.prismic.preview", preview_token)
    return response