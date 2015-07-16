import logging as _logging, time
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from app import api
from app.models import Discipline, Team
from app.robot.key_generator import KeyGenerator

__author__ = 'fernando'

logging = _logging.getLogger("cache_updater")


class CacheHelper(KeyGenerator, object):
    def update_teams_index(self, modified_teams, excluded_teams, campus, semester):
        start = time.time()
        logging.debug("Updating teams index of the campus \o/")
        api.get_all_teams({
            "q": "anything",
            "campus": self.generate_campus_key(campus, semester)
        }, overwrite=True, index=True, update_with=modified_teams, exclude=excluded_teams)
        excluded_teams_keys = map(lambda team: ndb.Key(Team, team), excluded_teams)
        for excluded_team in excluded_teams:
            logging.debug("Deleting team '%s'", excluded_team)
            api.get_team(excluded_team, overwrite=True, exclude=True)
        ndb.Future.wait_all(map(ndb.Key.delete_async, excluded_teams_keys))
        logging.debug("Search (and update) of teams made in %f seconds", time.time() - start)
        modified_teams = []
        excluded_teams = []
        return modified_teams, excluded_teams

    def update_disciplines_index(self, campus, semester, modified_disciplines, excluded_disciplines):
        start = time.time()
        logging.debug("Indexing all the disciplines of the campus \o/")
        api.get_disciplines({
            "campus": self.generate_campus_key(campus, semester),
            "q": "anything"
        }, overwrite=True, index=True, update_with=modified_disciplines, exclude=excluded_disciplines)
        modified_disciplines_teams = []
        for modified_discipline in modified_disciplines:
            modified_disciplines_teams.append({
                "id": self.generate_discipline_key(modified_discipline, campus, semester),
                "teams": map(ndb.Key.id, modified_discipline.teams)
            })
        api.get_disciplines_teams({
            "q": "anything",
            "campus": self.generate_campus_key(campus, semester)
        }, overwrite=True, index=True, update_with=modified_disciplines_teams, exclude=excluded_disciplines)
        excluded_disciplines_keys = map(lambda discipline: ndb.Key(Discipline, discipline), excluded_disciplines)
        for excluded_discipline in excluded_disciplines:
            logging.debug("Deleting discipline '%s'", excluded_discipline)
            discipline = api.get_discipline(excluded_discipline)
            self.update_teams_index([], map(lambda team: str(team.id()), discipline.teams), campus, semester)
            api.get_discipline(excluded_discipline, overwrite=True, exclude=True)
        ndb.Future.wait_all(map(ndb.Key.delete_async, excluded_disciplines_keys))
        logging.debug("Search (and update) of disciplines made in %f seconds", time.time() - start)
        modified_disciplines = []
        excluded_disciplines = []
        return modified_disciplines, excluded_disciplines

    def update_campi_cache(self, modified_campi, semester):
        logging.debug("Updating campi cache of the semester")
        semester_key = self.generate_semester_key(semester)
        campi = api.get_campi({"semester": semester_key})
        new_campi = []
        modified = []
        for campus in campi:
            for modified_campus in modified_campi:
                if campus.key == modified_campus.key:
                    new_campi.append(modified_campus["model"])
                    modified.append(modified_campus["key"])
                    break
            else:
                new_campi.append(campus)
        for modified_campus in modified_campi:
            if modified_campus["key"] in modified:
                continue
            new_campi.append(modified_campus)
        api.get_campi({"semester": semester_key}, overwrite=True, update_with=new_campi)
        modified_campi = []
        return modified_campi

    def update_semester_cache(self, semester_key):
        logging.debug("Updating semesters cache")
        semesters = api.get_semesters({})
        new_semesters = []
        found = False
        for semester in semesters:
            if not semester:
                continue
            if semester.key == semester_key["key"]:
                new_semesters.append(semester_key["model"])
                found = True
            else:
                new_semesters.append(semester)
        if not found:
            # If the semester is new..Insert it into the start of the array
            new_semesters.insert(0, semester_key["model"])
        print new_semesters
        api.get_semesters({}, overwrite=True, update_with=new_semesters)

    def check_cache_existence(self, team, campus, semester):
        logging.warn("Checking cache existence")
        disciplines_results = api.get_disciplines({
            "campus": self.generate_campus_key(campus, semester),
            "q": team.discipline.code
        })
        if not disciplines_results["results"]:
            logging.warn("Creating disciplines cache for allow use in the fast searches")
            api.get_disciplines({
                "campus": self.generate_campus_key(campus, semester),
                "q": team.discipline.code
            }, index=True, overwrite=True)
        disciplines_teams_results = api.get_disciplines_teams({
            "q": self.generate_discipline_key(team.discipline, campus, semester).replace("matrufsc2-discipline-", ""),
            "campus": self.generate_campus_key(campus, semester)
        })
        if not disciplines_teams_results["results"] or not disciplines_teams_results["results"][0].get("teams"):
            logging.warn("Creating disciplines-teams cache for allow use in the fast searches")
            api.get_disciplines_teams({
                "q": self.generate_discipline_key(team.discipline, campus, semester).replace("matrufsc2-discipline-", ""),
                "campus": self.generate_campus_key(campus, semester)
            }, index=True, overwrite=True)
        teams_results = api.get_all_teams({
            "q": self.generate_team_key(team, campus, semester).replace("matrufsc2-team-", ""),
            "campus": self.generate_campus_key(campus, semester)
        })
        if not teams_results["results"]:
            logging.warn("Creating teams cache for allow use in the fast searches")
            api.get_all_teams({
                "q": self.generate_team_key(team, campus, semester).replace("matrufsc2-team-", ""),
                "campus": self.generate_campus_key(campus, semester)
            }, index=True, overwrite=True)
