from app.robot.fetcher.auth.BaseAuth import BaseAuth
import os

__author__ = 'fernando'


class EnvAuth(BaseAuth):
    __slots__ = ["key"]

    def __init__(self, key):
        self.key = key

    def get_password(self):
        user, password = os.environ.get(self.key).split(":", 1)
        password = password.decode("base64")
        return password

    def has_data(self):
        return os.environ.has_key(self.key)

    def get_username(self):
        user, password = os.environ.get(self.key).split(":", 1)
        return user