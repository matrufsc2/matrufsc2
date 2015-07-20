from google.appengine.api import app_identity
from app.cache import get_from_cache, set_into_cache

__author__ = 'fernando'


def get_domain():
    domain = get_from_cache("matrufsc2_domain").get_result()
    if not domain:
        domain = app_identity.get_default_version_hostname()
        set_into_cache("matrufsc2_domain", domain).get_result()
    return domain
