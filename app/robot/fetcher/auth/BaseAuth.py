__author__ = 'fernando'

class BaseAuth(object):

    def has_data(self):
        raise NotImplementedError()

    def get_username(self):
        raise NotImplementedError()

    def get_password(self):
        raise NotImplementedError()