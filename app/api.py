from app.repositories import CampusRepository, DisciplinesRepository, TeamsRepository, TeachersRepository, \
    SchedulesRepository, SemesterRepository
from google.appengine.ext import ndb

__author__ = 'fernando'


def get_campi(filters):
    repository = CampusRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


def get_campus(idValue):
    repository = CampusRepository()
    return repository.find_by_id(idValue)


def get_semesters(filters):
    repository = SemesterRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


def get_semester(idValue):
    repository = SemesterRepository()
    return repository.find_by_id(idValue)


def get_disciplines(filters):
    repository = DisciplinesRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


def get_discipline(idValue):
    repository = DisciplinesRepository()
    return repository.find_by_id(idValue)


def get_teams(filters):
    repository = TeamsRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


def get_team(idValue):
    repository = TeamsRepository()
    return repository.find_by_id(idValue)


def get_teachers(filters):
    repository = TeachersRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


def get_teacher(idValue):
    repository = TeachersRepository()
    return repository.find_by_id(idValue)


def get_schedules(filters):
    repository = SchedulesRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


def get_schedule(idValue):
    repository = SchedulesRepository()
    return repository.find_by_id(idValue)