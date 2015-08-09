import pickle
import urllib
import logging
import zlib
import time
from app.robot.fetcher.base import BaseFetcher
from google.appengine.ext import ndb

logging = logging.getLogger("NDBRemoteFetcher")

__author__ = 'fernando'


class NDBRemoteFetcher(BaseFetcher):
    __slots__ = ["last_data", "last_page_number", "base_url"]

    def __init__(self, base_url):
        self.last_data = None
        self.last_page_number = 1
        self.base_url = base_url

    @ndb.tasklet
    def __fetch_request(self, path):
        parameters = {}
        if self.last_data:
            parameters.update(self.last_data.copy())
        parameters["page_number"] = self.last_page_number
        url = self.base_url % path
        logging.debug("Requesting remote fetcher via NDB with parameters %s to URL %s", repr(parameters), url)
        ctx = ndb.get_context()
        for _ in xrange(3):
            try:
                handler = yield ctx.urlfetch(
                    url=url,
                    payload=urllib.urlencode(parameters),
                    method="POST",
                    headers={'Cache-Control': 'no-cache,max-age=0', 'Pragma': 'no-cache'},
                    allow_truncated=False,
                    deadline=60,
                    follow_redirects=False
                )
            except:
                time.sleep(1)
                continue
            content = handler.content
            result = pickle.loads(zlib.decompress(content))
            if isinstance(result, Exception):
                raise result
            raise ndb.Return(result)

    @ndb.tasklet
    def login(self):
        result = yield self.__fetch_request("login")
        raise ndb.Return(result)

    @ndb.tasklet
    def has_next_page(self):
        result = yield self.__fetch_request("has_next_page")
        raise ndb.Return(result)

    @ndb.tasklet
    def fetch_campi(self):
        result = yield self.__fetch_request("fetch_campi")
        raise ndb.Return(result)

    @ndb.tasklet
    def fetch_semesters(self):
        result = yield self.__fetch_request("fetch_semesters")
        raise ndb.Return(result)

    @ndb.tasklet
    def fetch_teams(self):
        result = yield self.__fetch_request("fetch_teams")
        raise ndb.Return(result)

    @ndb.tasklet
    def fetch(self, data=None, page_number=1):
        self.last_data = data
        self.last_page_number = page_number
        raise ndb.Return()