import urllib
import zlib
from app.robot.fetcher.base import BaseFetcher
try:
    import cPickle as pickle
except:
    import pickle

__author__ = 'fernando'

class RemoteFetcher(BaseFetcher):
    __slots__ = ["last_data", "last_page_number", "base_url"]

    def __init__(self, base_url):
        self.last_data = None
        self.last_page_number = 1
        self.base_url = base_url

    def __fetch_request(self, path):
        parameters = {}
        if self.last_data:
            parameters.update(self.last_data.copy())
        parameters["page_number"] = self.last_page_number
        handler = urllib.urlopen(self.base_url%path, urllib.urlencode(parameters))
        content = handler.read()
        result = pickle.loads(zlib.decompress(content))
        if isinstance(result, Exception):
            raise result
        return result

    def login(self):
        return self.__fetch_request("login")

    def has_next_page(self):
        return self.__fetch_request("has_next_page")

    def fetch_campi(self):
        return self.__fetch_request("fetch_campi")

    def fetch_semesters(self):
        return self.__fetch_request("fetch_semesters")

    def fetch_teams(self):
        return self.__fetch_request("fetch_teams")

    def fetch(self, data=None, page_number=1):
        self.last_data = data
        self.last_page_number = page_number
