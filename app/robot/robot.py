import hashlib
import logging as _logging
import time
from app.models import Campus, Semester, Schedule, Discipline, Team, Teacher
from app.repositories import CampusRepository, SemesterRepository, DisciplinesRepository, TeamsRepository
from app.robot.fetcher.NDBRemoteFetcher import NDBRemoteFetcher
from google.appengine.ext import ndb
from google.appengine.api import taskqueue, modules

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'fernando'

logging = _logging.getLogger("robot")

context = ndb.get_context()
context_options = ndb.ContextOptions(use_cache=False, use_memcache=False)

class Robot(NDBRemoteFetcher, object):
    def __init__(self, base_url):
        """
        Initializes the robot

        :param base_url: The base url to use in the requests to fetcher
        :type base_url: selenium.webdriver.remote.webdriver.WebDriver
        """
        super(Robot, self).__init__(base_url)

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

    @ndb.tasklet
    def register_semesters(self, semesters):
        logging.info("Registering semesters..")
        repository = SemesterRepository()
        result = []
        found_ids = []
        to_put = []
        logging.debug("Finding all semesters found in the page..")
        to_get = repository.find_by({
            "key": map(self.generate_semester_key, semesters)
        }).iter()
        """ :type: google.appengine.ext.ndb.QueryIterator """
        while (yield to_get.has_next_async()):
            semester = to_get.next()
            """ :type: app.models.Semester """
            semester_id = None
            for semester_data in semesters:
                if semester_data.name == semester.name:
                    semester_id = semester_data.id
                    break
            if semester_id is None:
                raise Exception("Not found semester")
            result.append({
                "id": semester_id,
                "name": semester.name,
                "new": False,
                "key": semester.key
            })
            found_ids.append(semester_id)
        for semester in semesters:
            if semester.id in found_ids:
                continue
            logging.debug("Saving semesters to be put in the database..")
            to_put.append(Semester(key=ndb.Key(Semester, self.generate_semester_key(semester)), name=semester.name))
        logging.debug("Saving semesters in the database...")
        new_keys = yield ndb.put_multi_async(to_put)
        for semester_key, semester_model in zip(new_keys, to_put):
            semester_id = None
            for semester_data in semesters:
                if semester_data.name == semester_model.name:
                    semester_id = semester_data.id
                    break
            if semester_id is None:
                raise Exception("Not found semester")
            result.append({
                "id": semester_id,
                "name": semester_model.name,
                "new": True,
                "key": semester_key
            })
            found_ids.append(semester_id)
        assert len(found_ids) == len(semesters), "Not found all semesters (%d != %d)" % (len(found_ids), len(semesters))
        raise ndb.Return(result)

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
            "semester_id": semester['id'],
            "semester_name": semester['name'],
            "name": campus.name
        }
        key = "matrufsc2-campus-%s" % hashlib.sha1(key).hexdigest()
        return key

    @ndb.tasklet
    def register_campi(self, campi, semesters):
        logging.info("Registering campi..")
        repository = CampusRepository()
        result = []

        for campus_data in campi:
            logging.debug("Finding all semesters related to a campus..")
            to_get = repository.find_by({
                "key": map(lambda semester: self.generate_campus_key(campus_data, semester), semesters)
            }).iter()
            """ :type to_get: google.appengine.ext.ndb.QueryIterator """
            to_put = []
            found_semesters = []
            while (yield to_get.has_next_async()):
                campus = to_get.next()
                semester = None
                for semester_data in semesters:
                    if campus.semester.id() == semester_data['key'].id():
                        semester = semester_data
                        break
                if semester is None:
                    raise Exception("Not found semester")
                result.append({
                    "id": campus_data.id,
                    "name": campus_data.name,
                    "semester_id": semester['id'],
                    "semester_key": semester['key'],
                    "new": False,
                    "key": campus.key
                })
                found_semesters.append(semester['id'])
            for semester in semesters:
                if semester['id'] in found_semesters:
                    continue
                logging.debug("Registering campus to be saved...")
                to_put.append(Campus(
                    key=ndb.Key(Campus, self.generate_campus_key(campus_data, semester)),
                    name=campus_data.name,
                    semester=semester['key']
                ))
            logging.debug("Saving campi..")
            new_keys = yield ndb.put_multi_async(to_put)
            for campus_key, campus_model in zip(new_keys, to_put):
                """ :type campus_model: app.models.Campus """
                semester = None
                for semester_data in semesters:
                    if semester_data['key'].id() == campus_model.semester.id():
                        semester = semester_data
                        break
                if semester is None:
                    raise Exception("Not found semester")
                result.append({
                    "id": campus_data.id,
                    "name": campus_data.name,
                    "semester_id": semester['id'],
                    "semester_key": semester['key'],
                    "new": True,
                    "key": campus_key
                })
                found_semesters.append(semester['id'])
            assert len(found_semesters) == len(semesters), "Not found all semesters"
        raise ndb.Return(result)

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
        logging.debug("Searching schedule '%s' in cache", key)
        value = yield context.memcache_get(key)
        if value is not None:
            raise ndb.Return(value)
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
        logging.debug("Saving schedule '%s' in cache", key)
        yield context.memcache_set(key, schedule_model.key)
        raise ndb.Return(schedule_model.key)

    def generate_teacher_key(self, teacher):
        """
        Gets a teacher key to use to save cache and other nice things

        :param teacher: The teacher to base the key on
        :return: The key of the teacher
        ;rtype: str
        """
        key = "%(teacher_name)s"% {
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
        logging.debug("Searching teacher '%s' in cache", teacher.name.decode("ISO-8859-1"))
        value = yield context.memcache_get(key)
        if value:
            raise ndb.Return(value)
        logging.debug("Searching (or even registering) teacher '%s' in NDB", teacher.name.decode("ISO-8859-1"))
        teacher_model = yield Teacher.get_or_insert_async(
            key,
            name=teacher.name.decode("ISO-8859-1"),
            context_options=context_options
        )
        """ type: app.models.Teacher """
        logging.debug("Saving teacher '%s' in cache", teacher.name.decode("ISO-8859-1"))
        yield context.memcache_set(key, teacher_model.key)
        raise ndb.Return(teacher_model.key)

    def generate_discipline_key(self, discipline, campus):
        """
        Gets a discipline key to use to save the cache and other nice things

        :param discipline: The discipline to base the key on
        :param campus: The campus to base the key on
        :return: The key of the discipline
        ;rtype: str
        """
        key = '%(campus)s-%(discipline_code)s' % {
            "campus": campus["key"].id(),
            "discipline_code": discipline.code
        }
        key = "matrufsc2-discipline-%s" % hashlib.sha1(key).hexdigest()
        return key

    @ndb.tasklet
    def get_discipline_key(self, discipline, campus):
        """
        Get (or create) the discipline key based on the data of discipline and campus

        :param discipline: The discipline data
        :type discipline: app.robot.value_objects.Discipline
        :param campus: The campus data
        :return: The discipline key
        :rtype: google.appengine.ext.ndb.Key
        """
        logging.debug("Searching discipline '%s' in cache", discipline.code)
        key = self.generate_discipline_key(discipline, campus)
        value = yield context.memcache_get(key)
        if value is not None:
            raise ndb.Return(value)
        logging.debug("Searching (or even registering) discipline '%s' in NDB", discipline.code)
        discipline_model = yield Discipline.get_or_insert_async(
            key,
            code=discipline.code,
            name=discipline.name,
            campus=campus['key'],
            context_options=context_options
        )
        """ type: app.models.Discipline """
        logging.debug("Saving discipline '%s' in cache", discipline.code)
        yield context.memcache_set(key, discipline_model.key)
        raise ndb.Return(discipline_model.key)

    def generate_team_key(self, team, campus):
        """
        Generate a team key to use with cache and other nice things

        :param team: The team which the key is based on
        :param campus: The campus which the key is based on
        :return: The key generated for the team
        :rtype: str
        """
        key = '%(semester_id)s-%(campus)s-%(discipline_code)s-%(team_code)s'% {
            "semester_id": campus['semester_key'].id(),
            'campus': campus['key'].id(),
            'discipline_code': team.discipline.code,
            'team_code': team.code
        }
        key = "matrufsc2-team-%s" % hashlib.sha1(key).hexdigest()
        return key

    @ndb.tasklet
    def process_team(self, team, campus):
        """
        Get (or create) a team and return its model instance

        :param team: The team data
        :param campus: The campus data
        :return: The team model
        :rtype: app.models.Team
        """
        logging.debug("Getting information about team %s in campus %s and semesters %s", team.code, campus['name'],
                      campus['semester_id'])
        key = self.generate_team_key(team, campus)
        logging.debug("Searching for team '%s' in cache", team.code)
        team_model, discipline_key, teachers, schedules = yield (
            context.memcache_get(key),
            self.get_discipline_key(team.discipline, campus),
            map(self.get_teacher_key, team.teachers),
            map(self.get_schedule_key, team.schedules)
        )
        """ :type: app.models.Team|None """
        db_key = ndb.Key(Team, key)
        if team_model is not None:
            logging.debug("Team '%s' found in cache", team.code)
        else:
            logging.debug("Searching team '%s' in database", team.code)
            team_model = yield db_key.get_async(options=context_options)
            """ :type: app.models.Team """
        modified = False
        if team_model:
            if team_model.vacancies_offered != team.vacancies_offered:
                team_model.vacancies_offered = team.vacancies_offered
                modified = True
            if team_model.vacancies_filled != team.vacancies_filled:
                team_model.vacancies_filled = team.vacancies_filled
                modified = True
            if team_model.teachers != teachers:
                team_model.teachers = teachers
                modified = True
            if team_model.schedules != schedules:
                team_model.schedules = schedules
                modified = True
        else:
            team_model = Team(
                key=db_key,
                code=team.code,
                discipline=discipline_key,
                vacancies_offered=team.vacancies_offered,
                vacancies_filled=team.vacancies_filled,
                teachers=teachers,
                schedules=schedules
            )
            modified = True
        if modified:
            logging.debug("Saving team '%s' on NDB and on cache", team.code)
            yield team_model.put_async(options=context_options), context.memcache_set(key, team_model)
        else:
            logging.debug("Saving team '%s' in cache", team.code)
            yield context.memcache_set(key, team_model)

    @ndb.tasklet
    def fetch_page(self, page_number, semester, campus):
        """
        Fetch the page.

        :param page_number: The page number to process
        :type page_number: int
        :param semester: The semester to request
        :param campus: The campus to request
        :return: google.appengine.ext.ndb.Future
        """
        logging.debug("Setting parameters of the request...")
        yield self.fetch({
            "selectSemestre": semester["id"],
            "selectCampus": campus["id"],
        }, page_number)
        logging.info("Processing page")
        teams = yield self.fetch_teams()
        logging.debug("Processing %d teams", len(teams))
        has_next = yield self.has_next_page()
        raise ndb.Return({
            "teams_to_process": teams,
            "has_next": has_next
        })

    @ndb.tasklet
    def clean_old_data(self, semesters):
        """
        Clean old data fro mthe database

        :return:
        """
        disciplines_repository = DisciplinesRepository()
        campi_repository = CampusRepository()
        teams_repository = TeamsRepository()
        logging.info(
            "Deleting data from the recent semesters: %s",
            ", ".join(map(lambda semester: semester["name"], semesters[:1])),
        )
        logging.debug("Finding campus referenced by the semester..")
        campus_keys = yield campi_repository.find_by({
            "semester": map(lambda semester: semester["key"].id(), semesters[:1])
        }).fetch_async(keys_only=True)
        to_remove = []
        for campus_key in campus_keys:
            logging.debug("Finding disciplines referenced by the campus..")
            discipline_keys = yield disciplines_repository.find_by({
                "campus": campus_key.id()
            }).fetch_async(keys_only=True)
            for discipline_key in discipline_keys:
                logging.debug("Finding teams referenced by the discipline..")
                teams_keys = yield teams_repository.find_by({
                    "discipline": discipline_key.id()
                }).fetch_async(keys_only=True)
                to_remove.extend(teams_keys)
                to_remove.append(discipline_key)
        logging.info("Deleting everything related (%d objects) to the recent two semesters", len(to_remove))
        yield ndb.delete_multi_async(to_remove)

    @ndb.tasklet
    def run(self, params):
        """
        Run the robot \o/

        :return: google.appengine.ext.ndb.Future
        """
        timeout = 540
        if modules.get_current_module_name() == "robot":
            logging.info("Detected that we are at 'robot' module <3")
            timeout = 3600
        logging.info("The timeout of this request is of %d seconds", timeout)
        timeout = time.time() + timeout
        if params:
            params = pickle.loads(params)
            page_number = params["page_number"]
            semester = params["semester"]
            campus = params["campus"]
            logging.info("Processing campus %s and semester %s..", campus['name'], semester['name'])
            yield self.login()
            while True:
                logging.info("Processing page %d", page_number)
                data = yield self.fetch_page(page_number, semester, campus)
                has_next = data["has_next"]
                teams_to_process = data["teams_to_process"]
                for count, team in enumerate(teams_to_process, start=1):
                    logging.info("Processing team %d of %d total teams", count, len(teams_to_process))
                    yield self.process_team(team, campus)
                    if time.time() >= timeout:
                        raise Exception("Houston, we have a problem. [I this is more fucking slow than Windows]")
                if has_next:
                    page_number += 1
                    if time.time() >= timeout:
                        raise Exception("Houston, we have a problem. [I this is more fucking slow than Windows]")
                else:
                    logging.info("Flushing all the things :D")
                    yield context.flush()
                    logging.info("All the things is flushed :D")
                    break
        else:
            semesters_data, campi_data = yield self.fetch_semesters(), self.fetch_campi()
            semesters = yield self.register_semesters(semesters_data)
            campi = yield self.register_campi(campi_data, semesters)
            yield self.clean_old_data(semesters)
            count_semesters = 0
            for semester in semesters:
                if count_semesters >= 1 and not semester['new']:
                    logging.warn("Ignoring semester %s as it's not new to database and its not recent too",
                                 semester['name'])
                    continue
                for campus in campi:
                    logging.info("Processing semester %s..", semester['name'])
                    if campus['semester_id'] != semester['id']:
                        logging.debug("Ignoring campus with different semester")
                        continue
                    logging.info("Processing campus %s and semester %s..", campus['name'], semester['name'])
                    page_number = 1
                    logging.debug("Scheduling task..")
                    taskqueue.add(url="/secret/update/", payload=pickle.dumps({
                        "page_number": page_number,
                        "semester": semester,
                        "campus": campus
                    }), method="POST")
                count_semesters += 1

        raise ndb.Return("OK")
