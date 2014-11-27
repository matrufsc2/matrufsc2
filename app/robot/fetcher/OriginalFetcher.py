from bs4 import BeautifulSoup
import urllib2
import urllib
import cookielib
import gzip
import re
import logging
import unicodedata
from app.robot.fetcher.base import BaseFetcher
from app.robot.value_objects import Campus, Semester, Team, Schedule, Teacher, Discipline

try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree
logging = logging.getLogger("OriginalFetcher")

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

__author__ = 'fernando'

class OriginalFetcher(BaseFetcher):
    """
    Fetcher inspired on the [original fetcher](https://github.com/ramiropolla/matrufsc_dbs/blob/master/py/get_turmas.py)
    created by Ramiro Polla
    """

    __slots__ = ["opener", "auth", "xml", "buffer", "base_request", "view_state"]

    def __init__(self, auth, opener=urllib2.build_opener(
        urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
        urllib2.HTTPSHandler(debuglevel=0)
    )):
        """
        Initializes the fetcher

        :param auth: The authenticator to use
        :type auth: app.robot.fetcher.auth.BaseAuth.BaseAuth
        :param opener: The opener to use to connect to CAGR
        """
        self.opener = opener
        self.auth = auth
        self.buffer = ""
        self.base_request = None
        self.xml = None
        self.view_state = None
        self.login()

    def login(self):
        """
        Do login in CAGR
        """
        if not self.auth or not self.auth.has_data():
            raise Exception("OriginalFetcher needs auth data")
        logging.info("Doing login \o/")
        resp = self.opener.open('https://cagr.sistemas.ufsc.br/modules/aluno')
        soup = BeautifulSoup(resp)
        url_action = soup.form['action']
        login_form = {}
        for input in soup.findAll('input'):
            try:
                login_form[input['name']] = input['value']
            except KeyError:
                pass
        login_form['username'] = self.auth.get_username()
        login_form['password'] = self.auth.get_password()
        logging.debug("Sending login form..")
        self.opener.open('https://sistemas.ufsc.br' + url_action, urllib.urlencode(login_form))
        logging.info('Getting view state')
        resp = self.opener.open('https://cagr.sistemas.ufsc.br/modules/aluno/cadastroTurmas/')
        soup = BeautifulSoup(resp)
        self.view_state = soup.find('input', {'name':'javax.faces.ViewState'})['value']
        self.base_request = urllib2.Request('https://cagr.sistemas.ufsc.br/modules/aluno/cadastroTurmas/index.xhtml')
        self.base_request.add_header('Accept-encoding', 'gzip')

    def fetch(self, data=None, page_number=1):
        form_data = {
            'AJAXREQUEST': '_viewRoot',
            'formBusca:selectSemestre': '',
            'formBusca:selectDepartamento': '',
            'formBusca:selectCampus': '',
            'formBusca:selectCursosGraduacao': '0',
            'formBusca:codigoDisciplina': '',
            'formBusca:j_id135_selection': '',
            'formBusca:filterDisciplina': '',
            'formBusca:j_id139': '',
            'formBusca:j_id143_selection': '',
            'formBusca:filterProfessor': '',
            'formBusca:selectDiaSemana': '0',
            'formBusca:selectHorarioSemana': '',
            'formBusca': 'formBusca',
            'autoScroll': '',
            'javax.faces.ViewState': self.view_state,
            'AJAX:EVENTS_COUNT': '1',
        }
        name_form = "formBusca"
        data['dataScroller1'] = str(page_number)
        for key, value in data.iteritems():
            key = ":".join([name_form, key])
            form_data[key] = value
        logging.debug("Doin request...")
        resp = self.opener.open(self.base_request, urllib.urlencode(form_data))
        logging.debug("Reading data...")
        if resp.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(resp.read())
            f = gzip.GzipFile(fileobj=buf)
            self.buffer = f.read()
        else:
            self.buffer = resp.read()
        logging.debug("Parsing XML..")
        self.xml = ElementTree.fromstring(self.buffer)

    def fetch_campi(self):
        campi = [ 'EaD', 'FLO', 'JOI', 'CBS', 'ARA', 'BLN' ]
        return [Campus(**{
                    "id": campus_id,
                    "name": campi[campus_id]
                }) for campus_id in range(1, len(campi))]

    def fetch_semesters(self):
        semesters = ["20142", "20151"]
        return [Semester(**{
                    "id": semester,
                    "name": "-".join([semester[:4], semester[4:]])
                }) for semester in semesters]

    def find_id(self, element_id, parent=None):
        if parent is None:
            parent = self.xml
        for element in parent:
            if element.get('id') == element_id:
                return element
            else:
                element = self.find_id(element_id, element)
                if element is not None:
                    return element

    def has_next_page(self):
        scroller = self.find_id('formBusca:dataScroller1_table')
        if scroller is None:
            return False
        for x in scroller[0][0]:
            onclick = x.get('onclick')
            if onclick is not None and 'next' in onclick:
                return True
        return False

    def fetch_teams(self):
        if not self.buffer:
            return []
        teams = []
        schedule_re = re.compile(
            "(?P<dayOfWeek>\d)\.(?P<hourStart>\d{2})(?P<minuteStart>\d{2})\-(?P<numberOfLessons>\d) \/ (?P<room>.+)")
        for row in self.xml[1][1][2]:
            team = {}
            team["code"] = row[4].text # str

            team["vacancies_offered"] = int(row[7].text) # int
            try:
                saldo_vagas   = int(row[10].text) # int or <span>LOTADA</span>
            except TypeError:
                saldo_vagas   = 0
            team["vacancies_filled"] = team["vacancies_offered"] - saldo_vagas

            schedules_rows = []   # str split by <br />, may be emtpy
            if row[12].text:
                schedules_rows.append(row[12].text)
            for sub in row[12]:
                if sub.tail:
                    schedules_rows.append(sub.tail)

            schedules = []

            for schedule_row in schedules_rows:
                if not schedule_row:
                    continue
                match = schedule_re.match(schedule_row.strip())
                if not match:
                    # logging.debug("The following schedule row has not matched: %s", schedule_row)
                    continue
                obj = match.groupdict()
                obj['dayOfWeek'] = int(obj['dayOfWeek'])
                obj['hourStart'] = int(obj['hourStart'])
                obj['minuteStart'] = int(obj['minuteStart'])
                obj['numberOfLessons'] = int(obj['numberOfLessons'])
                schedules.append(Schedule(**obj))
            team["schedules"] = schedules

            teachers = []    # str split by <br />, may be emtpy, some
                                # entries may be inside <a>
            if len(row[13]):
                if not row[13][0].text:
                    teachers.append(row[13].text)
            
            for sub in row[13]:
                if sub.attrib:
                    teachers.append(sub.text)
                elif sub.tail:
                    teachers.append(sub.tail)
            team["teachers"] = map(
                    lambda teacher_name: Teacher(name=teacher_name),
                    filter(
                        None,
                        map(
                            str.strip,
                            map(
                                lambda s: str(s.encode("ISO-8859-1")),
                                teachers
                            )
                        )
                    )
                )

            discipline = {}
            discipline["code"] = row[3].text # str
            nome_disciplina   = row[5].text # str split by <br />
            for sub in row[5]:
                nome_disciplina = nome_disciplina + ' ' + sub.tail

            try:    # nome_disciplina may be str or unicode
                nome_disciplina_ascii = unicodedata.normalize('NFKD', nome_disciplina).encode('ascii', 'ignore')
            except TypeError:
                nome_disciplina_ascii = nome_disciplina
            discipline["name"] = nome_disciplina_ascii

            team["discipline"] = Discipline(**discipline)
            teams.append(Team(**team))
        return teams
