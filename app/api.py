import logging

from app.repositories import CampusRepository, DisciplinesRepository, TeamsRepository, SemesterRepository
from app.decorators import cacheable, searchable


__author__ = 'fernando'

logging = logging.getLogger("matrufsc2_api")

@cacheable(consider_only=[])
def get_semesters(filters):
    repository = SemesterRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()

@cacheable()
def get_semester(id_value):
    repository = SemesterRepository()
    return repository.find_by_id(id_value).get_result()

@cacheable(consider_only=["semester"])
def get_campi(filters):
    repository = CampusRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()

@cacheable()
def get_campus(id_value):
    repository = CampusRepository()
    return repository.find_by_id(id_value).get_result()

@searchable
@cacheable(consider_only=['campus'])
def get_disciplines(filters):
    repository = DisciplinesRepository()
    if filters:
        disciplines = repository.find_by(filters).get_result()
    else:
        disciplines = repository.find_all().get_result()
    for discipline in disciplines:
        discipline.teams = []
    return disciplines


@cacheable()
def get_discipline(id_value):
    repository = DisciplinesRepository()
    discipline = repository.find_by_id(id_value).get_result()
    discipline.teams = []
    return discipline

@cacheable(consider_only=["discipline"])
def get_teams(filters):
    repository = TeamsRepository()
    if filters:
        return repository.find_by(filters).get_result()
    return repository.find_all().get_result()


@cacheable()
def get_team(id_value):
    repository = TeamsRepository()
    return repository.find_by_id(id_value).get_result()