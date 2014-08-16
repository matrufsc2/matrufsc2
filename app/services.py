from Cookie import Cookie, SimpleCookie
import logging
import urllib
from app.models import Campus, Semester, Schedule, Discipline, Team, Teacher
from app.repositories import CampusRepository, SemesterRepository, DisciplinesRepository, TeamsRepository
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from bs4 import BeautifulSoup
__author__ = 'fernando'
import re

class Robot(object):
    BASE_URL = "http://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/index.xhtml"
    cookie = SimpleCookie()
    @ndb.tasklet
    def doRequest(self, data = None):
        logging.debug("Doing request with '%s' query parameters..", urllib.urlencode(data) if data else 'None')
        context = ndb.get_context()
        headers = {}
        if data:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Cookie'] = ""
        for value in self.cookie.values():
            headers['Cookie'] += "%s=%s;" % (value.key, value.value)
        print headers
        request = yield context.urlfetch(
            self.BASE_URL,
            urllib.urlencode(data) if data else None,
            urlfetch.POST if data else urlfetch.GET,
            headers=headers,
            follow_redirects=False,
            allow_truncated=False
        )
        for cookie in request.header_msg.getheaders("set-cookie"):
            self.cookie.load(cookie)
        content = request.content
        print "Conteudo: "
        print content
        print "Termino do conteudo"
        raise ndb.Return(BeautifulSoup(content))

    def getDataForRequest(self, semester, campus, page, viewState):
        return {
            'AJAX:EVENTS_COUNT': '1',
            'AJAXREQUEST': '_viewRoot',
            'formBusca': 'formBusca',
            'formBusca:dataScroller1': page,
            'formBusca:selectCampus': campus,
            'formBusca:selectCursosGraduacao': '0',
            'formBusca:selectDiaSemana': '0',
            'formBusca:selectSemestre': semester,
            'javax.faces.ViewState': viewState
        }

    @ndb.tasklet
    def fetchInformation(self):
        logging.info("Fetching basic information..")
        page = yield self.doRequest()
        raise ndb.Return({
            "campi": self.fetchCampi(page),
            "semesters": self.fetchSemesters(page),
            "viewState": self.fetchViewState(page)
        })

    def fetchCampi(self, page):
        logging.debug("Fetching campi in the page..")
        select = page.find("select", {
            "id": "formBusca:selectCampus"
        })
        return [[option.get("value"), option.get_text()] for option in select.find_all("option")]

    def fetchSemesters(self, page):
        logging.debug("Fetching semesters in the page..")
        select = page.find("select", {
            "id": "formBusca:selectSemestre"
        })
        return [[option.get("value"), option.get_text()] for option in select.find_all("option")]

    def fetchViewState(self, page):
        value = page.find('input', {'name':'javax.faces.ViewState'}).get("value", None)
        logging.info("Detecting that the javax.faces.ViewState is %s",value)
        return value

    def hasNext(self, page):
        logging.debug("Checking if there is a next page..")
        table = page.find("table", {
            "id": "formBusca:dataScroller1_table"
        })
        if table is None:
            return False
        columns = table.find_all("td")
        for column in columns:
            onclick = column.get('onclick')
            if onclick is not None and 'next' in onclick:
                logging.debug("Found 'next' page link in column onclick handler: %s", onclick)
                return True
        logging.debug("Not found 'next' page link in %d columns", len(columns))
        return False

    @ndb.tasklet
    def registerSemesters(self, semesters):
        logging.info("Registering semesters..")
        repository = SemesterRepository()
        result = []
        for semester_id, semester_name in semesters:
            logging.debug("Searching for semester %s", semester_name)
            key = yield repository.findBy({
                "name": semester_name
            }).get_async(keys_only=True)
            if not key:
                logging.debug("Semester not found, registering semester in NDB")
                key = yield Semester(name=semester_name).put_async()
            result.append([{"id":semester_id,"name":semester_name}, key])
        raise ndb.Return(result)

    @ndb.tasklet
    def registerCampi(self, campi, semesters):
        logging.info("Registering campi..")
        repository = CampusRepository()
        result = []
        for semester, semester_key in semesters:
            for campus_id, campus_name in campi:
                logging.debug("Searching for campus %s", campus_name)
                key = yield repository.findBy({
                    "name": campus_name,
                    "semester": semester_key.integer_id()
                }).get_async(keys_only=True)
                if not key:
                    logging.debug("Campus not found, registering campus in NDB")
                    key = yield Campus(name=campus_name, semester=semester_key).put_async()
                result.append([{
                   "id": campus_id,
                   "name": campus_name,
                   "semester_id": semester['id'],
                   "semester_key": semester_key
                }, key])
        raise ndb.Return(result)

    @ndb.tasklet
    def getScheduleKey(self, scheduleData):
        logging.debug("Searching schedule")
        schedule = yield Schedule.query(
            Schedule.hourStart==scheduleData["hourStart"],
            Schedule.minuteStart==scheduleData["minuteStart"],
            Schedule.numberOfLessons==scheduleData["numberOfLessons"],
            Schedule.dayOfWeek==scheduleData["dayOfWeek"],
            Schedule.room==scheduleData["room"]
        ).get_async(keys_only=True)
        if not schedule:
            logging.debug("Registering schedule in NDB")
            schedule = yield Schedule(
                hourStart=scheduleData["hourStart"],
                minuteStart=scheduleData["minuteStart"],
                numberOfLessons=scheduleData["numberOfLessons"],
                dayOfWeek=scheduleData["dayOfWeek"],
                room=scheduleData["room"]
            ).put_async()
        raise ndb.Return(schedule)

    @ndb.tasklet
    def getTeacherKey(self, teacherName):
        logging.debug("Searching teacher")
        teacher = yield Teacher.query(
            Teacher.name==teacherName
        ).get_async(keys_only=True)
        if not teacher:
            logging.debug("Registering teacher in NDB")
            teacher = yield Teacher(
                name=teacherName
            ).put_async()
        raise ndb.Return(teacher)

    @ndb.tasklet
    def processPage(self, page, campus_key, semester_name, campus_name, check_teams=True):
        if not page:
            logging.debug("Ignoring page without content")
            raise ndb.Return([])
        logging.info("Processing page")
        table = page.find("table", {
            "id": "formBusca:dataTable"
        })
        if not table:
            logging.debug("Not found table in the page, ignoring")
            raise ndb.Return([])
        tbody = table.find("tbody")
        rows = tbody.find_all("tr")
        schedule_re = re.compile("(?P<dayOfWeek>\d)\.(?P<hourStart>\d{2})(?P<minuteStart>\d{2})\-(?P<numberOfLessons>\d) \/ (?P<room>.+)")
        discipline_key = None
        discipline_code = None
        discipline_repository = DisciplinesRepository()
        team_repository = TeamsRepository()
        for row in rows:
            columns = row.find_all("td")
            if len(columns) < 14:
                logging.error("Ignoring row with only %d columns", len(columns))
                continue
            logging.debug("Processing team %d in semester %s and campus %s", int(columns[0].get_text()), semester_name, campus_name)
            discipline = {
                "code": columns[3].get_text(),
                "name": columns[5].get_text()
            }
            if discipline_code != discipline["code"]:
                logging.debug("Found different discipline code: Processing %s",discipline["code"])
                discipline_key = yield discipline_repository.findBy({
                    "code": discipline["code"],
                    "campus": campus_key.integer_id()
                }).get_async(keys_only=True)
                discipline_code = discipline["code"]
                if not discipline_key:
                    logging.debug("Not found discipline %s in database, registering it in NDB", discipline["code"])
                    discipline_key = yield Discipline(
                        code=discipline["code"],
                        name=discipline["name"],
                        campus=campus_key
                    ).put_async()
            team = {
                "code": columns[4].get_text(),
                "vacancies_offered": int(columns[7].get_text()),
                "vacancies_filled": int(columns[8].get_text())
            }
            if check_teams:
                logging.debug("Searching for team")
                team_model = yield team_repository.findBy({
                    "discipline": discipline_key.integer_id(),
                    "code": team["code"]
                }).get_async()
            else:
                team_model = None
            if not team_model:
                logging.debug("Team not found, registering it in NDB")
                team_model = Team(
                    code=team["code"],
                    discipline=discipline_key
                )
            team_model.vacancies_offered = team["vacancies_offered"]
            team_model.vacancies_filled = team["vacancies_filled"]
            logging.debug("Analyzing schedules of the team %s", team["code"])
            schedules = []
            schedules_rows = filter(None, map(str.strip, map(str, columns[12].get_text().split("\n"))))
            for schedule_row in schedules_rows:
                match = schedule_re.match(schedule_row)
                if not match:
                    # logging.debug("The following schedule row has not matched: %s", schedule_row)
                    continue
                obj = match.groupdict()
                obj['dayOfWeek'] = int(obj['dayOfWeek'])
                obj['hourStart'] = int(obj['hourStart'])
                obj['minuteStart'] = int(obj['minuteStart'])
                obj['numberOfLessons'] = int(obj['numberOfLessons'])
                schedules.append(obj)
            teachers_names = filter(None, map(str.strip, map(str, columns[13].get_text().split("\n"))))
            team_model.schedules = yield map(self.getScheduleKey, schedules)
            logging.debug("Analyzing teachers of the team %s", team["code"])
            team_model.teachers = yield map(self.getTeacherKey, teachers_names)
            yield team_model.put_async()
    @ndb.tasklet
    def run(self):
        information = yield self.fetchInformation()
        semesters = yield self.registerSemesters(information["semesters"])
        campi = yield self.registerCampi(information["campi"], semesters)
        first_semester = True
        disciplines_repository = DisciplinesRepository()
        campi_repository = CampusRepository()
        teams_repository = TeamsRepository()
        for semester, semester_key in semesters:
            logging.info("Processing semester %s..", semester['name'])
            if first_semester:
                logging.info("Deleting data from the semester %s",semester['name'])
                logging.debug("Finding campus referenced by the semester..")
                campus_keys = yield campi_repository.findBy({
                    "semester": semester_key.integer_id()
                }).fetch_async(keys_only=True)
                to_remove = []
                for campus_key in campus_keys:
                    logging.debug("Finding disciplines referenced by the campus..")
                    discipline_keys = yield disciplines_repository.findBy({
                        "campus": campus_key.integer_id()
                    }).fetch_async(keys_only=True)
                    for discipline_key in discipline_keys:
                        logging.debug("Finding teams referenced by the discipline..")
                        teams_keys = yield teams_repository.findBy({
                            "discipline": discipline_key.integer_id()
                        }).fetch_async(keys_only=True)
                        to_remove.extend(teams_keys)
                        to_remove.append(discipline_key)
                    to_remove.append(campus_key)
                logging.info("Deleting everything related to the semester %s",semester['name'])
                yield ndb.delete_multi_async(to_remove)
            for campus, campus_key in campi:
                if campus['semester_id'] != semester['id']:
                    logging.debug("Ignoring campus with different semester")
                    continue
                logging.debug("Defining new instance of cookie")
                self.cookie = SimpleCookie()
                logging.info("Processing campus %s and semester %s..",campus['name'],semester['name'])
                page_number = 1
                page = None
                while True:
                    logging.info("Processing page %d", page_number)
                    data = self.getDataForRequest(semester["id"], campus["id"], page_number, information["viewState"])
                    page, new_entities = yield (
                        self.doRequest(data),
                        self.processPage(page, campus_key, semester['name'], campus['name'], first_semester),
                    )
                    if not self.hasNext(page):
                        yield self.processPage(page, campus_key, semester['name'], campus['name'], first_semester)
                        break
                    page_number += 1
            first_semester = False