from app.exceptions import FieldNotFound
from app.models import Semester, Campus, Discipline, Team, Teacher, Schedule
from google.appengine.ext import ndb
from google.appengine.ext.ndb.model import KeyProperty, Key

__author__ = 'fernando'

class Repository:
    def findBy(self, filters):
        raise NotImplementedError("Repository.findBy not implemented")

    def findAll(self):
        raise NotImplementedError("Repository.findAll not implemented")

class NDBRepository(Repository):
    __model__ = None
    __keys__ = {}
    def __getModel__(self):
        if not self.__model__:
            raise NotImplementedError("Define a model in the repository")
        return self.__model__

    def __createFilter__(self, filters):
        filters = dict(filters.iteritems())
        model = self.__getModel__()
        if not filters:
            return []
        result = []
        if "id" in filters:
            del filters["id"]
        for key, value in filters.iteritems():
            if not hasattr(model, key):
                raise FieldNotFound("Field not found in the model: %s"%key)
            if self.__keys__.has_key(key):
                value = Key(self.__keys__.get(key), int(value))
            attr = getattr(model, key)
            result.append(attr == value)
        return ndb.AND(*result)

    def findBy(self, filters):
        return self.__getModel__().query(self.__createFilter__(filters))

    def findByID(self, idValue):
        return self.__getModel__().get_by_id(idValue)

    def findAll(self):
        return self.__getModel__().query()

class SemesterRepository(NDBRepository):
    __model__ = Semester

class CampusRepository(NDBRepository):
    __model__ = Campus
    __keys__ = {
        "semester": Semester
    }

class DisciplinesRepository(NDBRepository):
    __model__ = Discipline
    __keys__ = {
        "campus": Campus
    }

class TeamsRepository(NDBRepository):
    __model__ = Team
    __keys__ = {
        "discipline": Discipline
    }

class TeachersRepository(NDBRepository):
    __model__ = Teacher

class SchedulesRepository(NDBRepository):
    __model__ = Schedule
