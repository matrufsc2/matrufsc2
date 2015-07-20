from app.decorators.cacheable import cacheable
from app.repositories import SemesterRepository

__author__ = 'fernando'

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