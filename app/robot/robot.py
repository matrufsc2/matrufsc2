import collections
import time
import hashlib
import logging as _logging
import time
import math
from app.api import get_disciplines, get_semesters, get_campi
from app.models import Campus, Semester, Schedule, Discipline, Team, Teacher
from app.robot.fetcher.CommunityFetcher import CommunityFetcher
from app.robot.fetcher.NDBRemoteFetcher import NDBRemoteFetcher
from google.appengine.api.runtime.runtime import is_shutting_down
from google.appengine.ext import ndb
from google.appengine.api import taskqueue, modules
import cloudstorage as gcs
from google.appengine.api import app_identity
import urllib2, cookielib

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'fernando'

logging = _logging.getLogger("robot")

context = ndb.get_context()
context_options = ndb.ContextOptions(use_cache=False)


class Robot(CommunityFetcher, object):
    __slots__ = ["cookies"]

    def __init__(self):
        """
        Initializes the robot
        """
        self.cookies = cookielib.CookieJar()
        super(Robot, self).__init__(create_opener=lambda: urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookies),
            urllib2.HTTPSHandler(debuglevel=0)
        ))

    def generate_semester_key(self, semester):
        """
        Generate the semester key

        :param semester: The semester in which the key is based on
        :return: The key of the semester
        :rtype: str
        """
        key = "%(id)s-%(name)s" % {
            "id": semester.id,
            "name": semester.name
        }
        key = "matrufsc2-semester-%s" % hashlib.sha1(key).hexdigest()
        return key


    def generate_campus_key(self, campus, semester):
        """
        Generate the campus key

        :param campus: The campus in which the key is based on
        :param semester: The semester in which the key is based on
        :return: The key of the campus
        :rtype: str
        """
        key = "%(semester_id)s-%(semester_name)s-%(id)s-%(name)s" % {
            "id": campus.id,
            "semester_id": semester.id,
            "semester_name": semester.name,
            "name": campus.name
        }
        key = "matrufsc2-campus-%s" % hashlib.sha1(key).hexdigest()
        return key

    @ndb.tasklet
    def update_semester(self, semester, campus_keys):
        """
        Get (or create) the campus key based on which is available

        :param semester: The semester used to generate the key
        :param campus_keys: The campus to save in the database
        """
        logging.info("Saving/updating semester %s", semester.name)
        db_key = self.generate_semester_key(semester)
        campus_keys = list(sorted(campus_keys))
        logging.debug("Getting (or even inserting) semester from the database")
        semester_model = yield Semester.get_or_insert_async(
            db_key,
            name=semester.name,
            campi=campus_keys,
            context_options=context_options
        )
        """ :type: app.models.Semester """
        if list(sorted(semester_model.campi)) != campus_keys:
            logging.debug("Detected changed list of campus..saving it to the database..")
            semester_model.campi = campus_keys
            yield semester_model.put_async(options=context_options)
        raise ndb.Return(semester_model.key)

    @ndb.tasklet
    def get_campus_key(self, campus, semester, disciplines_keys):
        """
        Get (or create) the campus key based on which is available

        :param campus: The campus data to use in the creation
        :param semester: The semester used to generate the key
        :param disciplines_keys: The disciplines to save in the database
        :return: The key of the campus created (or updated in the database)
        """
        db_key = self.generate_campus_key(campus, semester)
        disciplines_keys = sorted(disciplines_keys)
        logging.debug("Getting (or even saving) campus '%s' on the database", campus.name)
        campus_model = yield Campus.get_or_insert_async(
            db_key,
            name=campus.name,
            disciplines=disciplines_keys,
            context_options=context_options
        )
        """ :type: app.models.Campus """
        if sorted(campus_model.disciplines) != disciplines_keys:
            logging.debug("Detected changed list of disciplines..saving it to the database..")
            campus_model.disciplines = disciplines_keys
            yield campus_model.put_async(options=context_options)
        raise ndb.Return(campus_model.key)


    def generate_schedule_key(self, schedule):
        """
        Gets a schedule key to use to save cache and other nice things

        :param schedule: The schedule to base the key on
        :return: The key of the schedule
        ;rtype: str
        """
        key = "%(hourStart)d-%(minuteStart)d-%(numberOfLessons)d-%(dayOfWeek)d-%(room)s" % {
            "hourStart": schedule.hourStart,
            "minuteStart": schedule.minuteStart,
            "numberOfLessons": schedule.numberOfLessons,
            "dayOfWeek": schedule.dayOfWeek,
            "room": schedule.room
        }
        key = "matrufsc2-schedule-%s" % hashlib.sha1(key).hexdigest()
        return key

    @ndb.tasklet
    def get_schedule_key(self, schedule):
        """
        Get (or create) the schedule key based on the schedule data

        :param schedule: The schedule data
        :type schedule: app.robot.value_objects.Schedule
        :return: The schedule key
        :rtype: google.appengine.ext.ndb.Key
        """
        key = self.generate_schedule_key(schedule)
        logging.debug("Searching (or even registering) schedule in NDB")
        schedule_model = yield Schedule.get_or_insert_async(
            key,
            hourStart=schedule.hourStart,
            minuteStart=schedule.minuteStart,
            numberOfLessons=schedule.numberOfLessons,
            dayOfWeek=schedule.dayOfWeek,
            room=schedule.room,
            context_options=context_options
        )
        """ type: app.models.Schedule """
        raise ndb.Return(schedule_model.key)

    def generate_teacher_key(self, teacher):
        """
        Gets a teacher key to use to save cache and other nice things

        :param teacher: The teacher to base the key on
        :return: The key of the teacher
        ;rtype: str
        """
        key = "%(teacher_name)s" % {
            "teacher_name": teacher.name
        }
        key = "matrufsc2-teacher-%s" % hashlib.sha1(key).hexdigest()
        return key

    @ndb.tasklet
    def get_teacher_key(self, teacher):
        """
        Get (or create) the teacher key based on the teacher name

        :param teacher: The teacher name
        :type teacher: app.robot.value_objects.Teacher
        :return: The teacher key
        :rtype: google.appengine.ext.ndb.Key
        """
        logging.debug("Searching teacher '%s'", teacher.name)
        key = self.generate_teacher_key(teacher)
        logging.debug("Searching (or even registering) teacher '%s' in NDB", teacher.name.decode("ISO-8859-1"))
        teacher_model = yield Teacher.get_or_insert_async(
            key,
            name=teacher.name.decode("ISO-8859-1"),
            context_options=context_options
        )
        """ type: app.models.Teacher """
        raise ndb.Return(teacher_model.key)

    def generate_discipline_key(self, discipline, campus, semester):
        """
        Gets a discipline key to use to save the cache and other nice things

        :param discipline: The discipline to base the key on
        :param campus: The campus to base the key on
        :param semester: The semester to base the key on
        :return: The key of the discipline
        :rtype: str
        """
        key = '%(semester)s-%(campus)s-%(discipline_code)s' % {
            "semester": semester.id,
            "campus": campus.id,
            "discipline_code": discipline.code
        }
        key = "matrufsc2-discipline-%s" % hashlib.sha1(key).hexdigest()
        return key

    @ndb.tasklet
    def get_discipline_key(self, discipline, campus, semester, teams_keys):
        """
        Create the discipline key based on the data of discipline and campus

        :param discipline: The discipline data
        :type discipline: app.robot.value_objects.Discipline
        :param campus: The campus data
        :type campus: app.robot.value_objects.Campus
        :param semester: The semester data
        :type semester: app.robot.value_objects.Semester
        :param teams_keys: The teams keys to add
        :return: The discipline key
        :rtype: google.appengine.ext.ndb.Key
        """
        logging.debug("Searching discipline '%s' in cache", discipline.code)
        key = self.generate_discipline_key(discipline, campus, semester)
        teams_keys = sorted(teams_keys)
        logging.debug("Searching (or even registering) discipline '%s' in NDB", discipline.code)
        discipline_model = yield Discipline.get_or_insert_async(
            key,
            code=discipline.code,
            name=discipline.name,
            teams=teams_keys,
            context_options=context_options
        )
        """ :type: app.models.Discipline """
        modified = False
        if discipline_model.name != discipline.name:
            discipline_model.name = discipline.name
            modified = True
        if sorted(discipline_model.teams) != teams_keys:
            discipline_model.teams = teams_keys
            modified = True
        if modified:
            logging.debug("The discipline has been modified....saving it to the database..")
            yield discipline_model.put_async(options=context_options)
        raise ndb.Return(discipline_model.key)

    def generate_team_key(self, team, campus, semester):
        """
        Generate a team key to use with cache and other nice things

        :param team: The team which the key is based on
        :param campus: The campus which the key is based on
        :param semester: The semester which the key is based on
        :return: The key generated for the team
        :rtype: str
        """
        key = '%(semester_id)s-%(campus)s-%(discipline_code)s-%(team_code)s' % {
            "semester_id": semester.id,
            'campus': campus.id,
            'discipline_code': team.discipline.code,
            'team_code': team.code
        }
        key = "matrufsc2-team-%s" % hashlib.sha1(key).hexdigest()
        return key

    @ndb.tasklet
    def get_team_key(self, team, campus, semester):
        """
        Get (or create) a team and return its model instance

        :param team: The team data
        :param campus: The campus data
        :return: The team model
        :rtype: app.models.Team
        """
        logging.debug("Getting information about team %s in campus %s and semesters %s", team.code, campus.name,
                      semester.name)
        key = self.generate_team_key(team, campus, semester)
        teachers, schedules = yield (
            map(self.get_teacher_key, team.teachers),
            map(self.get_schedule_key, team.schedules)
        )
        """ :type: app.models.Team|None """
        teachers = sorted(teachers)
        schedules = sorted(schedules)
        logging.debug("Searching (or even registering) team '%s' in database", team.code)
        team_model = yield Team.get_or_insert_async(
            key,
            code=team.code,
            vacancies_offered=team.vacancies_offered,
            vacancies_filled=team.vacancies_filled,
            teachers=teachers,
            schedules=schedules,
            context_options=context_options
        )
        """ :type: app.models.Team """
        modified = False
        if team_model.vacancies_offered != team.vacancies_offered:
            team_model.vacancies_offered = team.vacancies_offered
            modified = True
        if team_model.vacancies_filled != team.vacancies_filled:
            team_model.vacancies_filled = team.vacancies_filled
            modified = True
        if sorted(team_model.teachers) != teachers:
            team_model.teachers = teachers
            modified = True
        if sorted(team_model.schedules) != schedules:
            team_model.schedules = schedules
            modified = True
        if modified:
            logging.debug("Saving team '%s' on NDB and on cache", team.code)
            yield team_model.put_async(options=context_options)
        raise ndb.Return(team_model.key)

    @ndb.tasklet
    def fetch_page(self, page_number, semester, campus):
        """
        Fetch the page.

        :param page_number: The page number to process
        :type page_number: int
        :param semester: The semester to request
        :param campus: The campus to request
        :rtype: google.appengine.ext.ndb.Future
        """
        logging.debug("Setting parameters of the request...")
        yield self.fetch({
                             "selectSemestre": semester.id,
                             "selectCampus": campus.id
                         }, page_number)
        logging.info("Processing page")
        teams = yield self.fetch_teams()
        logging.debug("Processing %d teams", len(teams))
        has_next = yield self.has_next_page()
        raise ndb.Return({
            "teams_to_process": teams,
            "has_next": has_next
        })

    def calculate_timeout(self):
        timeout = 540
        if modules.get_current_module_name() == "robot":
            logging.info("Detected that we are at 'robot' module <3")
            timeout = 3600
        logging.info("The timeout of this request is of %d seconds", timeout)
        timeout = time.time() + timeout
        return timeout

    def clear_gcs_cache(self):
        logging.info("Clearing GCS cache..")
        retry = gcs.RetryParams(
            initial_delay=0.2,
            max_delay=2.0,
            backoff_factor=2,
            max_retry_period=15,
            urlfetch_timeout=60
        )
        bucket_name = app_identity.get_default_gcs_bucket_name()
        bucket = "/" + bucket_name
        folder = "/".join([bucket, "cache"])
        file_instances = gcs.listbucket(folder, retry_params=retry)
        for file_instance in file_instances:
            logging.debug("Deleting file %s", file_instance.filename)
            gcs.delete(file_instance.filename, retry_params=retry)
        logging.debug("GCS cache cleaned")

    def update_cache(self):
        start = time.time()
        logging.debug("Loading semesters..")
        semesters = get_semesters({}, overwrite=True)
        logging.debug("Semesters loaded in %f seconds", time.time()-start)
        start = time.time()
        logging.debug("Loading campi..")
        campi = get_campi({
            "semester": [semesters[0].key.id()]
        }, overwrite=True)
        logging.debug("Campi loaded in %f seconds", time.time()-start)
        for campus in campi:
            start = time.time()
            logging.debug("Loading disciplines of the campus %s..", campus.name)
            get_disciplines({
                "campus": [campus.key.id()]
            }, overwrite=True)
            logging.debug("Disciplines loaded in %f seconds", time.time()-start)
            start = time.time()
            logging.debug("Indexing all the things \o/")
            get_disciplines({
                "campus": campus.key.id(),
                "q": ""
            }, overwrite=True, index=True)
            get_disciplines({
                "campus": campus.key.id(),
                "q": "anything"
            }, overwrite=True, index=True)
            logging.debug("Search (and update) made in %f seconds", time.time()-start)


    @ndb.tasklet
    def run_worker(self, params):
        timeout = self.calculate_timeout()
        params = pickle.loads(params)
        for cookie in params["cookies"]:
            self.cookies.set_cookie(cookie)
        self.view_state = params["view_state"]
        page_number = int(params["page_number"])
        semester = params["semester"]
        """ :type: app.robot.value_objects.Semester """
        campi = params["campi"]
        """ :type: collections.deque """
        campus = campi.popleft()
        discipline = params.get("discipline")
        last_login = params.get("last_login", 0)
        discipline_entity = params.get("discipline_entity")
        disciplines = params.get("disciplines", set())
        teams = params.get("teams", [])
        skip = params.get("skip")
        logging.info("Processing semester %s and campus %s..", semester.name, campus.name)
        if skip is not None:
            logging.info("Hooray! Seems like this is a resuming task...Go go go :D")
        else:
            logging.info("Hey! Found that this is not a resuming task...Cleaning old task :D")
        if (last_login + 600) < time.time():
            yield self.login()
            last_login = time.time()
        logging.info("Processing campus %s", campus.name)
        logging.info("Processing page %d", page_number)
        data = yield self.fetch_page(page_number, semester, campus)
        has_next = data["has_next"]
        teams_to_process = data["teams_to_process"]
        for count, team in enumerate(teams_to_process, start=1):
            if skip is not None:
                if skip >= count:
                    logging.warn("Ignoring team %d of %d total teams", count, len(teams_to_process))
                    continue
                else:
                    if team.discipline.code != discipline:
                        raise Exception(
                            "Unexpected discipline found: %(actual)s (expected %(expected)s)" %
                            {
                                "actual": team.discipline.code,
                                "expected": discipline
                            }
                        )
                    discipline = team.discipline
                    skip = None
            logging.info("Processing team %d of %d total teams", count, len(teams_to_process))
            team_key = yield self.get_team_key(team, campus, semester)
            if discipline == team.discipline.code:
                logging.debug("Appending team to the list of teams in a discipline")
                teams.append(team_key)
            else:
                if teams:
                    logging.debug("Saving discipline..")
                    yield self.get_discipline_key(
                        discipline_entity,
                        campus,
                        semester,
                        teams
                    )
                    disciplines.add(discipline)
                discipline_entity = team.discipline
                discipline = discipline_entity.code
                logging.debug("Detected new discipline: %s", discipline)
                teams = [team_key]
            if is_shutting_down():
                logging.warn("Detected shutdown of the instance. Preparing new task to the queue..")
                skip = count - len(teams)
                if skip < 0:
                    logging.debug("Hey, seems like we need to go some pages before...")
                    page_number_dif = math.ceil((skip * -1) / 50.0)
                    logging.debug("In total, seems like we need to go %d pages before", page_number_dif)
                    skip += page_number_dif * 50
                    logging.debug("And, in this page, we need to ignore %d items", skip)
                    page_number -= page_number_dif
                logging.debug("Hey, seems like we need to ignore %d items on the page %d", skip,
                              page_number)
                campi.appendleft(campus)
                taskqueue.add(url="/secret/update/", payload=pickle.dumps({
                    "page_number": page_number,
                    "semester": semester,
                    "campi": campi,
                    "skip": skip,
                    "discipline": discipline,
                    "disciplines": disciplines,
                    "last_login": last_login + 60,
                    "view_state": self.view_state,
                    "cookies": list(self.cookies)
                }, pickle.HIGHEST_PROTOCOL), method="POST")
                raise ndb.Return("PAUSED")
            if time.time() >= timeout:
                raise Exception("Houston, we have a problem. [This is more fucking slow than Windows]")
        logging.info("Flushing all the things :D")
        yield context.flush()
        logging.info("All the things is flushed :D")
        if has_next and page_number < 120:
            logging.info("Scheduling task to process the next page..(page %d)", page_number + 1)
            campi.appendleft(campus)
            taskqueue.add(url="/secret/update/", payload=pickle.dumps({
                "page_number": page_number + 1,
                "semester": semester,
                "campi": campi,
                "discipline": discipline,
                "discipline_entity": discipline_entity,
                "teams": teams,
                "disciplines": disciplines,
                "last_login": last_login + 60,
                "view_state": self.view_state,
                "cookies": list(self.cookies)
            }, pickle.HIGHEST_PROTOCOL), method="POST")
        else:
            if teams:
                logging.debug("Saving discipline..")
                yield self.get_discipline_key(discipline_entity, campus, semester, teams)
                disciplines.add(discipline)
            yield self.get_campus_key(
                campus,
                semester,
                (ndb.Key(Discipline, self.generate_discipline_key(Discipline(code=discipline), campus, semester))
                 for discipline in disciplines)
            )
            if campi:
                logging.debug("Hey, we have %d campus to process yet...registering...", len(campi))
                taskqueue.add(url="/secret/update/", payload=pickle.dumps({
                    "page_number": 1,
                    "semester": semester,
                    "campi": campi,
                    "last_login": last_login,
                    "view_state": self.view_state,
                    "cookies": list(self.cookies)
                }, pickle.HIGHEST_PROTOCOL), method="POST")
            else:
                taskqueue.add(url="/secret/clear_cache/", method="GET")

    @ndb.tasklet
    def run(self, params):
        """
        Run the robot \o/

        :return: google.appengine.ext.ndb.Future
        """
        if params:
            response = yield self.run_worker(params)
            if response:
                raise ndb.Return(response)
        else:
            semesters_data, campi_data = yield self.fetch_semesters(), self.fetch_campi()
            count_semesters = 0
            yield self.login()
            last_login = time.time()
            for semester in semesters_data:
                if count_semesters >= 1:
                    logging.warn("Ignoring semester %s as it's not new to database and its not recent too",
                                 semester['name'])
                    continue

                logging.info("Scheduling task for semester %s..", semester.name)
                taskqueue.add(url="/secret/update/", payload=pickle.dumps({
                    "page_number": 1,
                    "semester": semester,
                    "campi": collections.deque(campi_data),
                    "last_login": last_login,
                    "view_state": self.view_state,
                    "cookies": list(self.cookies)
                }, pickle.HIGHEST_PROTOCOL), method="POST")
                count_semesters += 1
                yield self.update_semester(semester, (ndb.Key(Campus, self.generate_campus_key(campus, semester))
                                                      for campus in campi_data))

        raise ndb.Return("OK")
