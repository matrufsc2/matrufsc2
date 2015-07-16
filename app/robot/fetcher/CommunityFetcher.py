from bs4 import BeautifulSoup
import urllib2
import cookielib
import logging
from app.robot.fetcher.OriginalFetcher import OriginalFetcher
from google.appengine.ext import ndb

try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree
logging = logging.getLogger("CommunityFetcher")

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

__author__ = 'fernando'


class CommunityFetcher(OriginalFetcher):
    """
    Fetcher inspired on the [original fetcher](https://github.com/ramiropolla/matrufsc_dbs/blob/master/py/get_turmas.py)
    created by Ramiro Polla
    """

    def __init__(self, create_opener=lambda: urllib2.build_opener(
        urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
        urllib2.HTTPSHandler(debuglevel=0)
    )):
        """
        Initializes the fetcher

        :param auth: The authenticator to use
        :type auth: app.robot.fetcher.auth.BaseAuth.BaseAuth
        :param opener: The opener to use to connect to CAGR
        """
        super(CommunityFetcher, self).__init__(None, create_opener)
        self.opener = self.create_opener()
        self.base_request = urllib2.Request('https://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/index.xhtml')
        self.base_request.add_header('Accept-Encoding', 'gzip')
        self.base_request.add_header("Referer", "https://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/")
        self.base_request.add_header("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
        self.base_request.add_header("User-Agent",
                                     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0")
        self.base_request.add_header("Pragma", "no-cache")
        self.base_request.add_header("Cache-Control", "no-cache")

    def login(self):
        """
        Do login in CAGR
        """
        logging.info('Getting view state')
        resp = self.opener.open('https://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/')
        soup = BeautifulSoup(resp)
        self.view_state = soup.find('input', {'name': 'javax.faces.ViewState'})['value']