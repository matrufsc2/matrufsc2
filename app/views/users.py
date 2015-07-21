from google.appengine.api import users
from app.views.api import serialize

__author__ = 'fernando'

def get_current_user():
    is_authenticated = users.get_current_user() is not None
    login_url = None
    logout_url = None
    if is_authenticated:
        logout_url = users.create_logout_url("/")
    else:
        login_url = users.create_login_url("/")
    return serialize({
        "id": "current",
        "is_authenticated": is_authenticated,
        "login_url": login_url,
        "logout_url": logout_url
    })


def get_users():
    is_authenticated = users.get_current_user() is not None
    login_url = None
    logout_url = None
    if is_authenticated:
        logout_url = users.create_logout_url("/")
    else:
        login_url = users.create_login_url("/")
    return serialize([{
        "id": "current",
        "is_authenticated": is_authenticated,
        "login_url": login_url,
        "logout_url": logout_url
    }])
