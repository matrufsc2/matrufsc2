import logging as _logging
import time
from app.models import Campus, Semester, Schedule, Discipline, Team, Teacher
from app.repositories import CampusRepository, SemesterRepository, DisciplinesRepository, TeamsRepository
from app.robot.fetcher.NDBRemoteFetcher import NDBRemoteFetcher
from google.appengine.ext import ndb
from google.appengine.api import taskqueue, memcache

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'fernando'

logging = _logging.getLogger("robot")

class Robot(NDBRemoteFetcher, object):
    def __init__(self, base_url):
        """
        Initializes the robot

        :param base_url: The base url to use in the requests to fetcher
        :type base_url: selenium.webdriver.remote.webdriver.WebDriver
        """
        super(Robot, self).__init__(base_url)

    @ndb.tasklet
    def register_semesters(self, semesters):
        logging.info("Registering semesters..")
        repository = SemesterRepository()
        result = []
        found_ids = []
        to_put = []
        logging.debug("Finding all semesters found in the page..")
        to_get = repository.find_by({
            "name": map(lambda semester: semester.name, semesters)
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
            to_put.append(Semester(name=semester.name))
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

    @ndb.tasklet
    def register_campi(self, campi, semesters):
        logging.info("Registering campi..")
        repository = CampusRepository()
        result = []

        for campus_data in campi:
            logging.debug("Finding all semesters related to a campus..")
            to_get = repository.find_by({
                "name": campus_data.name,
                "semester": map(lambda semester: semester['key'].integer_id(), semesters)
            }).iter()
            """ :type to_get: google.appengine.ext.ndb.QueryIterator """
            to_put = []
            found_semesters = []
            while (yield to_get.has_next_async()):
                campus = to_get.next()
                semester = None
                for semester_data in semesters:
                    if campus.semester.integer_id() == semester_data['key'].integer_id():
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
                to_put.append(Campus(name=campus_data.name, semester=semester['key']))
            logging.debug("Saving campi..")
            new_keys = yield ndb.put_multi_async(to_put)
            for campus_key, campus_model in zip(new_keys, to_put):
                """ :type campus_model: app.models.Campus """
                semester = None
                for semester_data in semesters:
                    if semester_data['key'].integer_id() == campus_model.semester.integer_id():
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

    @ndb.tasklet
    def get_schedule_key(self, schedule):
        """
        Get (or create) the schedule key based on the schedule data

        :param schedule: The schedule data
        :type schedule: app.robot.value_objects.Schedule
        :return: The schedule key
        :rtype: google.appengine.ext.ndb.Key
        """
        key = "matrufsc2-schedule-%(hourStart)d-%(minuteStart)d-%(numberOfLessons)d-%(dayOfWeek)d-%(room)s" % {
            "hourStart": schedule.hourStart,
            "minuteStart": schedule.minuteStart,
            "numberOfLessons": schedule.numberOfLessons,
            "dayOfWeek": schedule.dayOfWeek,
            "room": schedule.room
        }
        logging.debug("Searching schedule '%s'", key)
        if memcache.get(key) is not None:
            tries = 10
            while memcache.get(key) is False and tries >= 0:
                logging.debug("Awaiting schedule '%s' to be saved in cache", key)
                yield ndb.sleep(0.5)
                tries -= 1
            if tries >= 0:
                logging.debug("Found schedule '%s' in cache", key)
                raise ndb.Return(memcache.get(key))
        logging.debug("Setting schedule on cache just to guarantee consistence")
        memcache.add(key, False)
        schedule_key = yield Schedule.query(
            Schedule.hourStart == schedule.hourStart,
            Schedule.minuteStart == schedule.minuteStart,
            Schedule.numberOfLessons == schedule.numberOfLessons,
            Schedule.dayOfWeek == schedule.dayOfWeek,
            Schedule.room == schedule.room
        ).get_async(keys_only=True)
        if not schedule_key:
            logging.debug("Registering schedule in NDB")
            schedule_key = yield Schedule(
                hourStart=schedule.hourStart,
                minuteStart=schedule.minuteStart,
                numberOfLessons=schedule.numberOfLessons,
                dayOfWeek=schedule.dayOfWeek,
                room=schedule.room
            ).put_async()
        logging.debug("Saving schedule '%s' in cache", key)
        memcache.replace(key, schedule_key)
        raise ndb.Return(schedule_key)

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
        key = "matrufsc2-teacher-%(teacher_name)s"% {
            "teacher_name": teacher.name
        }
        if memcache.get(key) is not None:
            tries = 10
            while memcache.get(key) is False and tries >= 0:
                logging.debug("Awaiting teacher '%s' to be saved in cache", teacher.name)
                yield ndb.sleep(0.5)
                tries -= 1
            if tries >= 0:
                logging.debug("Teacher '%s' found in cache", teacher.name)
                raise ndb.Return(memcache.get(key))
        logging.debug("Setting teacher on cache just to guarantee consistence")
        memcache.add(key, False)
        teacher_key = yield Teacher.query(
            Teacher.name == teacher.name.decode("ISO-8859-1")
        ).get_async(keys_only=True)
        """ :type: google.appengine.ext.ndb.Key """
        if not teacher_key:
            logging.debug("Registering teacher '%s' in NDB", teacher.name)
            teacher_key = yield Teacher(
                name=teacher.name.decode("ISO-8859-1")
            ).put_async()
        logging.debug("Saving teacher '%s' in cache", teacher.name)
        memcache.replace(key, teacher_key)
        raise ndb.Return(teacher_key)

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
        key = 'matrufsc2-discipline-%(campus)s-%(discipline_code)s' % {
            "campus": campus["id"],
            "discipline_code": discipline.code
        }
        if memcache.get(key) is not None:
            tries = 10
            while memcache.get(key) is False:
                logging.debug("Awaiting discipline '%s' to be saved in cache", discipline.code)
                yield ndb.sleep(0.5)
                tries -= 1
            if tries >= 0:
                logging.debug("Discipline %s found in cache", discipline.code)
                raise ndb.Return(memcache.get(key))
        logging.debug("Setting discipline on cache just to guarantee consistence")
        memcache.add(key, False)
        discipline_repository = DisciplinesRepository()
        discipline_key = yield discipline_repository.find_by({
            "code": discipline.code,
            "campus": campus['key'].integer_id()
        }).get_async(keys_only=True)
        """ :type: google.appengine.ext.ndb.Key """
        if not discipline_key:
            logging.debug("Not found discipline %s in database, registering it in NDB", discipline.code)
            discipline_key = yield Discipline(
                code=discipline.code,
                name=discipline.name,
                campus=campus['key']
            ).put_async()
        logging.debug("Saving discipline '%s' in cache", discipline.code)
        memcache.replace(key, discipline_key)
        raise ndb.Return(discipline_key)

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
        discipline_key, teachers, schedules = yield (
            self.get_discipline_key(team.discipline, campus),
            map(self.get_teacher_key, team.teachers),
            map(self.get_schedule_key, team.schedules)
        )
        key = 'matrufsc2-team-%(semester_id)s-%(campus)s-%(discipline_code)s-%(team_code)s'% {
            "semester_id": campus['semester_id'],
            'campus': campus['id'],
            'discipline_code': team.discipline.code,
            'team_code': team.code
        }
        if memcache.get(key) is not None:
            logging.debug("Team '%s' found in cache", team.code)
            team_model = memcache.get(key)
            """ :type: app.models.Team """
        else:
            team_repository = TeamsRepository()
            logging.debug("Searching for team '%s'", team.code)
            team_model = yield team_repository.find_by({
                "discipline": discipline_key.integer_id(),
                "code": team.code
            }).get_async()
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
                code=team.code,
                discipline=discipline_key,
                vacancies_offered=team.vacancies_offered,
                vacancies_filled=team.vacancies_filled,
                teachers=teachers,
                schedules=schedules
            )
            modified = True
        if modified:
            logging.debug("Saving team '%s' on NDB", team.code)
            yield team_model.put_async()
        logging.debug("Saving team '%s' in cache", team.code)
        memcache.replace(key, team_model)
        raise ndb.Return(team_model)

    @ndb.tasklet
    def process_page(self, page_number, semester, campus):
        """
        Process the page.

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
        result = []
        for team in teams:
            logging.debug("Adding team %s to the queue", team.code)
            result.append(self.process_team(team, campus))
        logging.debug("Processing %d teams", len(teams))
        _, has_next = yield result, self.has_next_page()
        logging.debug("Processed %d teams", len(teams))
        raise ndb.Return(has_next)

    @ndb.tasklet
    def run(self, params):
        """
        Run the robot \o/

        :return: google.appengine.ext.ndb.Future
        """
        if params:
            params = pickle.loads(params)
            page_number = params["page_number"]
            semester = params["semester"]
            campus = params["campus"]
            logging.info("Processing campus %s and semester %s..", campus['name'], semester['name'])
            timeout = time.time() + 540
            while True:
                logging.info("Processing page %d", page_number)
                has_next = yield self.process_page(page_number, semester, campus)
                if has_next:
                    page_number += 1
                    if time.time() >= timeout:
                        logging.debug("Scheduling page because of timeout..")
                        taskqueue.add(url="/secret/update/", payload=pickle.dumps({
                            "page_number": page_number,
                            "semester": semester,
                            "campus": campus
                        }), method="POST")
                        raise ndb.Return("QUEUED")
                else:
                    break
        else:

            semesters_data, campi_data = yield self.fetch_semesters(), self.fetch_campi()
            semesters = yield self.register_semesters(semesters_data)
            campi = yield self.register_campi(campi_data, semesters)
            count_semesters = 0
            disciplines_repository = DisciplinesRepository()
            campi_repository = CampusRepository()
            teams_repository = TeamsRepository()
            logging.info(
                "Deleting data from the recent two semesters: %s and %s",
                semesters[0]["name"],
                semesters[1]["name"]
            )
            logging.debug("Finding campus referenced by the semester..")
            campus_keys = yield campi_repository.find_by({
                "semester": map(lambda semester: semester["key"].integer_id(), semesters[:2])
            }).fetch_async(keys_only=True)
            to_remove = []
            for campus_key in campus_keys:
                logging.debug("Finding disciplines referenced by the campus..")
                discipline_keys = yield disciplines_repository.find_by({
                    "campus": campus_key.integer_id()
                }).fetch_async(keys_only=True)
                for discipline_key in discipline_keys:
                    logging.debug("Finding teams referenced by the discipline..")
                    teams_keys = yield teams_repository.find_by({
                        "discipline": discipline_key.integer_id()
                    }).fetch_async(keys_only=True)
                    to_remove.extend(teams_keys)
                    to_remove.append(discipline_key)
            logging.info("Deleting everything related (%d objects) to the recent two semesters", len(to_remove))
            yield ndb.delete_multi_async(to_remove)
            for semester in semesters:
                if count_semesters >= 2 and not semester['new']:
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

        raise ndb.Return("OK")
