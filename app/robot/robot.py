import collections
import json
import logging as _logging
from pprint import pprint
import random
import time
import math
from app.api import semesters, campi, disciplines as disciplines_module, teams as teams_module
from app.cache import lru_cache, clear_lru_cache, gc_collect
from app.decorators.threaded import threaded
from app.json_serializer import JSONEncoder
from app.models import Campus, Semester, Schedule, Discipline, Team, Teacher
from app.repositories import DisciplinesRepository
from app.robot import value_objects
from app.robot.fetcher.CommunityFetcher import CommunityFetcher
from google.appengine.api.runtime.runtime import is_shutting_down
from google.appengine.ext import ndb
from google.appengine.api import taskqueue, modules
import urllib2, cookielib
from app.robot.cache_helper import CacheHelper

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'fernando'

logging = _logging.getLogger("robot")
logging.setLevel(_logging.INFO)
context = ndb.get_context()
context_options = ndb.ContextOptions(use_cache=False)


class Robot(CommunityFetcher, CacheHelper, object):
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

    @ndb.tasklet
    def get_semester_key(self, semester, campus_keys):
        """
        Get (or create) the campus key based on which is available

        :param semester: The semester used to generate the key
        :param campus_keys: The campus to save in the database
        """
        logging.info("Saving/updating semester %s", semester.name)
        db_key = self.generate_semester_key(semester)
        modified = False
        logging.debug("Getting (or even inserting) semester from the database")
        semester_model = semesters.get_semester(db_key)
        if semester_model is None:
            semester_model = Semester(
                key=ndb.Key(Semester, db_key),
                name=semester.name,
                campi=[]
            )
        """ :type: app.models.Semester """
        if sorted(map(ndb.Key.id, semester_model.campi)) != sorted(map(ndb.Key.id, campus_keys)):
            modified = True
            logging.debug("Detected changed list of campus....")
            semester_model.campi = campus_keys
            logging.warning("Saving to NDB (saving semester '%s')", semester.name)
            yield semester_model.put_async(options=context_options)
            semesters.get_semester(db_key, overwrite=True, update_with=semester_model)
        raise ndb.Return({
            "modified": modified,
            "key": semester_model.key,
            "model": semester_model
        })

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
        logging.debug("Getting (or even saving) campus '%s' on the database", campus.name)
        modified = False
        campus_model = campi.get_campus(db_key)
        excluded_disciplines = []
        if campus_model is None:
            campus_model = Campus(
                key=ndb.Key(Campus, db_key),
                name=campus.name,
                disciplines=[]
            )
        """ :type: app.models.Campus """
        old_disciplines_ids = sorted(map(ndb.Key.id, campus_model.disciplines))
        new_disciplines_ids = sorted(map(ndb.Key.id, disciplines_keys))
        if old_disciplines_ids != new_disciplines_ids:
            excluded_disciplines.extend(
                filter(
                    lambda discipline_id: discipline_id not in new_disciplines_ids,
                    old_disciplines_ids
                )
            )
            logging.debug("Detected changed list of disciplines..")
            campus_model.disciplines = disciplines_keys
            logging.warning("Saving to NDB (saving campus '%s')", campus.name)
            yield campus_model.put_async(options=context_options)
            campi.get_campus(db_key, overwrite=True, update_with=campus_model)
        raise ndb.Return({
            "key": campus_model.key,
            "modified": modified,
            "model": campus_model,
            "excluded_disciplines": excluded_disciplines
        })

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
        logging.debug("Searching schedule...")
        schedule_model = lru_cache.get(key)
        if schedule_model:
            logging.debug("Found schedule in LRU cache :D")
            raise ndb.Return(ndb.Key(Schedule, key))
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
        lru_cache[key] = schedule_model
        raise ndb.Return(schedule_model.key)

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
        teacher_model = lru_cache.get(key)
        if teacher_model:
            logging.debug("Found teacher in LRU cache :D")
            raise ndb.Return(ndb.Key(Teacher, key))
        logging.debug("Searching (or even registering) teacher '%s' in NDB", teacher.name.decode("ISO-8859-1"))
        teacher_model = yield Teacher.get_or_insert_async(
            key,
            name=teacher.name.decode("ISO-8859-1"),
            context_options=context_options
        )
        """ type: app.models.Teacher """
        lru_cache[key] = teacher_model
        raise ndb.Return(teacher_model.key)

    @ndb.tasklet
    def get_discipline_key(self, discipline, campus, semester, teams_keys, old_teams, old_discipline):
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
        key = self.generate_discipline_key(discipline, campus, semester)
        modified = False
        discipline_model = None
        model_key = ndb.Key(Discipline, key)
        if old_discipline is None:
            logging.debug("Registering new discipline '%s' in NDB", discipline.code)
            # Well, no discipline found in search index, we need to create the discipline here
            discipline_model = Discipline(
                key=model_key,
                code=discipline.code,
                name=discipline.name,
                teams=teams_keys
            )
            # And of course update the old entitites to not let their think that this is not new =)
            old_discipline = json.loads(json.dumps(discipline_model, cls=JSONEncoder))
            old_teams = []
            modified = True
        else:
            logging.debug("Discipline '%s' found in cache :D", discipline.code)
        """ :type: app.models.Discipline """
        if old_discipline["name"] != discipline.name:
            logging.warn("The name of the discipline '%s' changed", discipline.code)
            logging.warn("%s != %s", old_discipline["name"], discipline.name)
            modified = True
        if sorted(map(str, old_teams)) != sorted(map(ndb.Key.id, teams_keys)):
            logging.warn("The list of teams of the discipline '%s' changed :~", discipline.code)
            logging.warn("%s != %s", sorted(map(str, old_teams)), sorted(map(ndb.Key.id, teams_keys)))
            modified = True
        if modified:
            logging.debug("The discipline '%s' has been modified....loading it from the cache...", discipline.code)
            # The discipline need to be get from the database (it already exists in the database, for sure)
            if discipline_model is None:
                discipline_model = disciplines_module.get_discipline(key)
            if discipline_model is None:
                logging.warning("For some reason the discipline was not found in cache and its not new..."
                                "Loading/recreating")
                discipline_model = yield Discipline.get_or_insert_async(
                    key,
                    code=discipline.code,
                    name=discipline.name,
                    teams=teams_keys,
                    context_options=context_options
                )
            discipline_model.name = discipline.name
            discipline_model.teams = teams_keys
            logging.warning("...and saving to NDB..(saving discipline '%s')", discipline.code)
            yield discipline_model.put_async(options=context_options)
            logging.debug("...and updating the cache..")
            disciplines_module.get_discipline(key, overwrite=True, update_with=discipline_model)
        raise ndb.Return({
            "modified": modified,
            "model": discipline_model,
            "key": model_key
        })

    @ndb.tasklet
    def get_team_key(self, team, campus, semester, team_old=None):
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
        model_key = ndb.Key(Team, key)
        modified = False
        team_model = None
        if team_old is None:
            logging.debug("Creating team '%s'", team.code)
            team_model = Team(
                key=ndb.Key(Team, key),
                code=team.code,
                vacancies_offered=team.vacancies_offered,
                vacancies_filled=team.vacancies_filled,
                teachers=[],
                schedules=[]
            )
            team_old = json.loads(json.dumps(team_model, cls=JSONEncoder))
            modified = True
        if str(team_old["vacancies_offered"]) != str(team.vacancies_offered):
            logging.warn("The vacancies offered of the team '%s' changed", team.code)
            logging.warn("%s != %s", str(team.vacancies_offered), str(team_old["vacancies_offered"]))
            modified = True
        if str(team_old["vacancies_filled"]) != str(team.vacancies_filled):
            logging.warn("The vacancies filled of the team '%s' changed", team.code)
            logging.warn("%s != %s", str(team.vacancies_filled), str(team_old["vacancies_filled"]))
            modified = True
        if sorted(map(self.generate_teacher_key, team.teachers)) != sorted(map(lambda teacher: str(teacher["id"]), team_old["teachers"])):
            logging.warn("The teachers list of the team '%s' changed", team.code)
            logging.warn("%s != %s", str(sorted(map(self.generate_teacher_key, team.teachers))), str(sorted(map(lambda teacher: str(teacher["id"]), team_old["teachers"]))))
            modified = True
        if sorted(map(self.generate_schedule_key, team.schedules)) != sorted(map(lambda schedule: str(schedule["id"]), team_old["schedules"])):
            logging.warn("The schedules list of the team '%s' changed", team.code)
            logging.warn("%s != %s", str(sorted(map(self.generate_schedule_key, team.schedules))), str(sorted(map(lambda schedule: str(schedule["id"]), team_old["schedules"]))))
            modified = True
        if modified:
            logging.warning("Saving to NDB (team '%s')", team.code)
            if team_model is None:
                team_model = teams_module.get_team(key)
            if team_model is None:
                logging.warning("For some reason the team was not found in cache and its not new...Loading/recreating")
                team_model = yield Team.get_or_insert_async(
                    key,
                    code=team.code,
                    vacancies_offered=team.vacancies_offered,
                    vacancies_filled=team.vacancies_filled,
                    teachers=[],
                    schedules=[],
                    context_options=context_options
                )
            team_model.vacancies_offered = team.vacancies_offered
            team_model.vacancies_filled = team.vacancies_filled
            if sorted(map(self.generate_teacher_key, team.teachers)) != sorted(map(lambda teacher: str(teacher["id"]), team_old["teachers"])):
                team_model.teachers = yield map(self.get_teacher_key, team.teachers)
            if sorted(map(self.generate_schedule_key, team.schedules)) != sorted(map(lambda schedule: str(schedule["id"]), team_old["schedules"])):
                team_model.schedules = yield map(self.get_schedule_key, team.schedules)
            yield team_model.put_async(options=context_options)
            teams_module.get_team(key, overwrite=True, update_with=team_model)
        raise ndb.Return({
            "model": team_model,
            "modified": modified,
            "key": model_key
        })

    @threaded
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
        self.fetch({
            "selectSemestre": semester.id,
            "selectCampus": campus.id
        }, page_number)
        logging.info("Fetching page %d" % page_number)
        start = time.time()
        teams = self.fetch_teams()
        logging.debug("Processing %d teams", len(teams))
        has_next = self.has_next_page()
        logging.debug("Processed page in %f seconds", time.time()-start)
        return {
            "teams_to_process": teams,
            "has_next": has_next
        }

    def calculate_timeout(self):
        timeout = 30
        if modules.get_current_module_name() == "robot":
            logging.info("Detected that we are at 'robot' module <3")
            timeout = 3600
        logging.info("The timeout of this request is of %d seconds", timeout)
        return timeout

    @ndb.tasklet
    def update_discipline(self, disciplines, modified_disciplines, discipline_entity, campus, semester, teams,
                          discipline_old_teams, excluded_teams):
        logging.debug("Searching discipline '%s' in the index of disciplines of the campus", discipline_entity.code)
        discipline_old = None
        discipline_old_search_more = True
        discipline_old_search_page = 1
        discipline_old_key = self.generate_discipline_key(discipline_entity, campus, semester)
        while discipline_old is None and discipline_old_search_more:
            logging.debug("Searching discipline in page %d", discipline_old_search_page)
            discipline_old_results = disciplines_module.get_disciplines({
                "campus": self.generate_campus_key(campus, semester),
                "q": discipline_entity.code,
                "limit": 5,
                "page": discipline_old_search_page
            })
            for result in discipline_old_results["results"]:
                if "".join(["matrufsc2-discipline-",result["id"]]) == discipline_old_key:
                    discipline_old = result
                    break
            if discipline_old is None:
                discipline_old_search_more = discipline_old_results["more"]
                if discipline_old_search_more:
                    discipline_old_search_page += 1
        discipline_old_teams_keys = map(lambda t: str(t["id"]), discipline_old_teams)
        teams_ids = map(lambda team_key: str(team_key.id()), teams)
        excluded_teams.extend(filter(lambda team_id: team_id not in teams_ids, discipline_old_teams_keys))
        logging.debug(
            "Found %d teams in cache for discipline '%s'",
            len(discipline_old_teams_keys),
            discipline_entity.code
        )
        if not discipline_old_teams_keys and discipline_old:
            logging.error("Found discipline '%s' without teams! Whatafucke?!?!?!", discipline_entity.code)
        discipline_key = yield self.get_discipline_key(
            discipline_entity,
            campus,
            semester,
            teams,
            discipline_old_teams_keys,
            discipline_old
        )
        if discipline_key["modified"]:
            logging.warn("Adding discipline to the list of modified disicplines")
            modified_disciplines.append(discipline_key["model"])
        disciplines.add(discipline_entity.code)
        raise ndb.Return((disciplines, modified_disciplines, excluded_teams))

    @ndb.tasklet
    def run_worker(self, params, tasks):
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
        old = params.get("old", False)
        registered_campi = params.get("registered_campi", [])
        discipline_teams = params.get("discipline_teams", [])
        discipline_old_teams = params.get("discipline_old_teams", [])
        modified_campi = params.get("modified_campi", [])
        excluded_teams = params.get("excluded_teams", [])
        modified_teams = params.get("modified_teams", [])
        modified_disciplines = params.get("modified_disciplines", [])
        skip = params.get("skip")
        logging.info("Processing semester %s and campus %s..", semester.name, campus.name)
        if skip is not None:
            logging.info("Hooray! Seems like this is a resuming task...Go go go :D")
        else:
            logging.info("Hey! Found that this is not a resuming task...Cleaning old task :D")
        if (last_login + 600) < time.time():
            self.login()
            last_login = time.time()
        logging.info("Processing campus %s", campus.name)
        logging.info("Processing page %d", page_number)
        if page_number == 0:
            team = None
            data = None
            if old:
                # Try to get row directly from the database to get sample team and test if the index is OK
                # Getting from the database is somewhat..costly, but its much less costly than getting 100+ pages
                # from CAGR to get pages from other campus too
                repository = DisciplinesRepository()
                disciplines = yield repository.find_by({
                    "campus": self.generate_campus_key(campus, semester)
                }, limit=10, keys_only=True)
                team_model = None
                discipline_model = None
                for discipline in disciplines:
                    discipline = yield discipline.get_async(use_cache=False, use_memcache=True)
                    for team in discipline.teams:
                        team_model = yield team.get_async(use_cache=False, use_memcache=True)
                        if team_model:
                            discipline_model = discipline
                            break
                    if discipline_model:
                        break
                if discipline_model and team_model:
                    # We successfully fetched some data from the database
                    # Now, ,we create value objects to pass to check_cache_existence test
                    discipline = value_objects.Discipline(
                        code=discipline_model.code,
                        name=discipline_model.name
                    )
                    team = value_objects.Team(
                        code=team_model.code,
                        discipline=discipline,
                        teachers=[],
                        vacancies_offered=team_model.vacancies_offered,
                        vacancies_filled=team_model.vacancies_filled,
                        schedules=[]
                    )
                else:
                    old = False
            if not old:
                data = self.fetch_page(page_number+1, semester, campus).get_result()
                team = random.choice(data["teams_to_process"])
            self.check_cache_existence(team, campus, semester)
            if old and campi:
                tasks.append(pickle.dumps({
                    "page_number": 0,
                    "semester": semester,
                    "campi": campi,
                    "last_login": last_login,
                    "view_state": self.view_state,
                    "cookies": list(self.cookies),
                    "old": old
                }, pickle.HIGHEST_PROTOCOL))
            elif not old:
                if not data:
                    logging.error("Possible bug found (this if should not run)")
                    data = self.fetch_page(page_number+1, semester, campus).get_result()
                campi.appendleft(campus)
                tasks.append(pickle.dumps({
                    "page_number": page_number + 1,
                    "semester": semester,
                    "campi": campi,
                    "registered_campi": registered_campi,
                    "last_login": last_login,
                    "view_state": self.view_state,
                    "modified_campi": modified_campi,
                    "cookies": list(self.cookies),
                    "data": data,
                    "old": old
                }, pickle.HIGHEST_PROTOCOL))
            if old:
                clear_lru_cache()
            raise ndb.Return("CHECKED")
        data = params["data"]
        has_next = data["has_next"]
        if has_next:
            next_data = self.fetch_page(page_number + 1, semester, campus)
        else:
            next_data = None
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
            logging.debug("Processing team %d of %d total teams", count, len(teams_to_process))
            if team.discipline.code != discipline:
                logging.debug("Detected new discipline, getting all the teams of that discipline...")
                discipline_old_teams = discipline_teams
                discipline_teams = teams_module.get_teams({
                    "discipline": self.generate_discipline_key(team.discipline, campus, semester),
                    "campus": self.generate_campus_key(campus, semester)
                })
            team_old = next((t for t in discipline_teams if t["code"] == team.code), None)
            if team_old:
                logging.debug(
                    "Located team '%s' in list of cached teams for discipline '%s' :D",
                    team.code,
                    team.discipline.code
                )
            else:
                logging.warn("Team '%s' not located in cache for discipline '%s'", team.code, team.discipline.code)
            team_key = yield self.get_team_key(team, campus, semester, team_old)
            if team_key["modified"]:
                logging.warn("Adding team '%s' to the list of modified teams", team.code)
                modified_teams.append(team_key["model"])
            team_key = team_key["key"]
            if discipline == team.discipline.code:
                logging.debug("Appending team to the list of teams in a discipline")
                teams.append(team_key)
            else:
                if teams:
                    disciplines, modified_disciplines, excluded_teams = yield self.update_discipline(
                        disciplines,
                        modified_disciplines,
                        discipline_entity,
                        campus,
                        semester,
                        teams,
                        discipline_old_teams,
                        excluded_teams
                    )
                discipline_entity = team.discipline
                discipline = discipline_entity.code
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
                payload = pickle.dumps({
                    "page_number": page_number,
                    "semester": semester,
                    "campi": campi,
                    "skip": skip,
                    "discipline": discipline,
                    "disciplines": disciplines,
                    "registered_campi": registered_campi,
                    "modified_disciplines": modified_disciplines,
                    "modified_campi": modified_campi,
                    "modified_teams": modified_teams,
                    "excluded_teams": excluded_teams,
                    "discipline_teams": discipline_teams,
                    "discipline_old_teams": discipline_old_teams,
                    "last_login": last_login + 60,
                    "view_state": self.view_state,
                    "cookies": list(self.cookies),
                    "data": params["data"]
                }, pickle.HIGHEST_PROTOCOL)
                while len(payload) >= 9e4:
                    if modified_teams or excluded_teams:
                        logging.debug("Saving %d modified teams and %d excluded teams", len(modified_teams), len(excluded_teams))
                        modified_teams, excluded_teams = self.update_teams_index(
                            modified_teams,
                            excluded_teams,
                            campus,
                            semester
                        )
                    elif modified_disciplines:
                        logging.debug("Saving %d modified disciplines", len(modified_disciplines))

                        modified_disciplines, excluded_disciplines = self.update_disciplines_index(
                            campus,
                            semester,
                            modified_disciplines,
                            []
                        )
                    elif modified_campi:
                        modified_campi = self.update_campi_cache(modified_campi, semester)
                    else:
                        logging.error("Well, we doing everything we can and nothing resolved the problem :(")
                        print pprint(pickle.loads(payload))
                        break
                    payload = pickle.dumps({
                        "page_number": page_number,
                        "semester": semester,
                        "campi": campi,
                        "skip": skip,
                        "discipline": discipline,
                        "disciplines": disciplines,
                        "registered_campi": registered_campi,
                        "modified_disciplines": modified_disciplines,
                        "modified_campi": modified_campi,
                        "modified_teams": modified_teams,
                        "excluded_teams": excluded_teams,
                        "discipline_teams": discipline_teams,
                        "discipline_old_teams": discipline_old_teams,
                        "last_login": last_login + 60,
                        "view_state": self.view_state,
                        "cookies": list(self.cookies),
                        "data": params["data"]
                    }, pickle.HIGHEST_PROTOCOL)
                taskqueue.add(url="/secret/update/", payload=payload, method="POST")
                raise ndb.Return("PAUSED")
        if has_next:
            logging.info("Scheduling task to process the next page..(page %d)", page_number + 1)
            campi.appendleft(campus)
            payload = pickle.dumps({
                "page_number": page_number + 1,
                "semester": semester,
                "campi": campi,
                "discipline": discipline,
                "discipline_entity": discipline_entity,
                "discipline_teams": discipline_teams,
                "discipline_old_teams": discipline_old_teams,
                "teams": teams,
                "disciplines": disciplines,
                "registered_campi": registered_campi,
                "modified_disciplines": modified_disciplines,
                "modified_teams": modified_teams,
                "modified_campi": modified_campi,
                "last_login": last_login + 60,
                "view_state": self.view_state,
                "cookies": list(self.cookies),
                "data": next_data.get_result()
            }, pickle.HIGHEST_PROTOCOL)
            while len(payload) >= 9e4:
                if modified_teams or excluded_teams:
                    logging.debug("Saving %d modified teams and %d excluded teams", len(modified_teams), len(excluded_teams))
                    modified_teams, excluded_teams = self.update_teams_index(
                        modified_teams,
                        excluded_teams,
                        campus,
                        semester
                    )
                elif modified_disciplines:
                    logging.debug("Saving %d modified disciplines", len(modified_disciplines))

                    modified_disciplines, excluded_disciplines = self.update_disciplines_index(
                        campus,
                        semester,
                        modified_disciplines,
                        []
                    )
                elif modified_campi:
                    modified_campi = self.update_campi_cache(modified_campi, semester)
                else:
                    logging.error("Well, we doing everything we can and nothing resolved the problem :(")
                    print pprint(pickle.loads(payload))
                    break
                payload = pickle.dumps({
                    "page_number": page_number + 1,
                    "semester": semester,
                    "campi": campi,
                    "discipline": discipline,
                    "discipline_entity": discipline_entity,
                    "discipline_teams": discipline_teams,
                    "discipline_old_teams": discipline_old_teams,
                    "teams": teams,
                    "disciplines": disciplines,
                    "registered_campi": registered_campi,
                    "modified_disciplines": modified_disciplines,
                    "modified_teams": modified_teams,
                    "modified_campi": modified_campi,
                    "excluded_teams": excluded_teams,
                    "last_login": last_login + 60,
                    "view_state": self.view_state,
                    "cookies": list(self.cookies),
                    "data": next_data.get_result()
                }, pickle.HIGHEST_PROTOCOL)
            tasks.append(payload)
        else:
            if teams:
                discipline_old_teams = discipline_teams
                disciplines, modified_disciplines, excluded_teams = yield self.update_discipline(
                    disciplines,
                    modified_disciplines,
                    discipline_entity,
                    campus,
                    semester,
                    teams,
                    discipline_old_teams,
                    excluded_teams
                )
            campus_key = yield self.get_campus_key(
                campus,
                semester,
                map(lambda code: ndb.Key(Discipline, self.generate_discipline_key(Discipline(code=code), campus, semester)), disciplines)
            )
            if campus_key["modified"]:
                modified_campi.append(campus_key["model"])
            excluded_disciplines = campus_key["excluded_disciplines"]
            campus_key = campus_key["key"]
            registered_campi.append(campus_key)
            if modified_teams or excluded_teams:
                logging.debug("Saving %d modified teams and %d excluded teams", len(modified_teams), len(excluded_teams))
                modified_teams, excluded_teams = self.update_teams_index(modified_teams, excluded_teams, campus, semester)
            if modified_disciplines or excluded_disciplines:
                logging.debug("Saving %d modified and %d excluded disciplines", len(modified_disciplines), len(excluded_disciplines))
                modified_disciplines, excluded_disciplines = self.update_disciplines_index(
                    campus,
                    semester,
                    modified_disciplines,
                    excluded_disciplines
                )
            if modified_campi:
                modified_campi = self.update_campi_cache(modified_campi, semester)
            if campi:
                logging.debug("Hey, we have %d campus to process yet...registering...", len(campi))
                tasks.append(pickle.dumps({
                    "page_number": 0,
                    "semester": semester,
                    "campi": campi,
                    "registered_campi": registered_campi,
                    "last_login": last_login,
                    "view_state": self.view_state,
                    "cookies": list(self.cookies)
                }, pickle.HIGHEST_PROTOCOL))
            else:
                semester_key = yield self.get_semester_key(semester, registered_campi)
                self.update_semester_cache(semester_key)
                # Clear LRU cache on the frontend
                taskqueue.add(url="/secret/clear_cache/", method="GET", queue_name="frontend", target="default")
            clear_lru_cache()
        logging.info("Flushing all the things :D")
        yield context.flush()
        logging.info("All the things is flushed :D")

    @ndb.tasklet
    def run(self, params):
        """
        Run the robot \o/

        :return: google.appengine.ext.ndb.Future
        """
        tasks = []
        if params:
            tasks.append(params)
        else:
            semesters_data, campi_data = self.fetch_semesters(), self.fetch_campi()
            self.login()
            last_login = time.time()
            for count_semesters, semester in enumerate(semesters_data):
                logging.info("Scheduling task for semester %s..", semester.name)
                tasks.append(pickle.dumps({
                    "page_number": 0,
                    "semester": semester,
                    "campi": collections.deque(campi_data),
                    "last_login": last_login,
                    "view_state": self.view_state,
                    "cookies": list(self.cookies),
                    "old": count_semesters >= 1
                }, pickle.HIGHEST_PROTOCOL))
        count = 0
        timeout = self.calculate_timeout()
        start = time.time()
        while tasks:
            gc_collect()
            passed_in = time.time()-start
            logging.info(
                "There are %d tasks to process (done %d tasks and %f seconds to timeout)",
                len(tasks),
                count,
                timeout-passed_in
            )
            params = tasks.pop()
            if passed_in >= timeout:
                logging.info("Adding task to the AppEngine's queue and closing request because of timeout")
                taskqueue.add(
                    url="/secret/update/",
                    payload=params,
                    method="POST",
                    queue_name="default",
                    target="robot"
                )
                continue
            if tasks:
                logging.warning("There are more than a task to process yet o.O")
            try:
                response = yield self.run_worker(params, tasks)
                logging.debug("The response of the task is: %s", response)
            except:
                logging.exception("Exception detected when running worker")
                break
            count += 1
            gc_collect()
        raise ndb.Return("OK")
