from app.exceptions import FieldNotFound
from app.models import Semester, Campus, Discipline, Team, Teacher, Schedule
from google.appengine.ext import ndb
from google.appengine.ext.ndb.model import Key

__author__ = 'fernando'


class Repository(object):
    def __init__(self):
        pass

    def find_by(self, filters):
        raise NotImplementedError("Repository.find_by not implemented")

    def find_all(self):
        raise NotImplementedError("Repository.find_all not implemented")


class NDBRepository(Repository):
    __model__ = None
    __keys__ = {}
    def __get_model__(self):
        """
        Returns the model on which this repository is based on

        :return: The model
        :rtype: google.appengine.ext.ndb.Model
        """
        if not self.__model__:
            raise NotImplementedError("Define a model in the repository")
        return self.__model__

    def __create_filter__(self, filters):
        filters = dict(filters.iteritems())
        model = self.__get_model__()
        if not filters:
            return []
        self.__keys__['key'] = model
        result = []
        if "id" in filters:
            del filters["id"]
        for key, value in filters.iteritems():
            if not hasattr(model, key):
                raise FieldNotFound("Field not found in the model: %s"%key)
            if self.__keys__.has_key(key):
                if isinstance(value, list):
                    value = map(
                        lambda item:
                            Key(self.__keys__.get(key), item if not item.isdigit() else int(item)),
                            value
                    )
                else:
                    value = Key(self.__keys__.get(key), value if not value.isdigit() else int(value))
            attr = getattr(model, key)
            if isinstance(value, list):
                result.append(attr.IN(value))
            else:
                result.append(attr == value)
        return ndb.AND(*result)

    def find_by(self, filters):
        """
        Created query based on the specified filters

        :param filters: The filters to use on the query
        :type filters: dict
        :return: The query of the App Engine
        :rtype: ndb.Query
        """
        return self.__get_model__().query(self.__create_filter__(filters))

    def find_by_id(self, id_value):
        """
        Get an unique model based on the specified id

        :param id_value: The ID of the element to get
        :type id_value: int|string
        :return: The query of the App Engine
        :rtype: ndb.Query
        """
        return self.__get_model__().get_by_id(id_value)

    def find_all(self):
        """
        Get all the models on the table

        :return: The query of the App Engine
        :rtype: ndb.Query
        """
        return self.__get_model__().query()


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

    def find_by(self, filters):
        """
        Created query based on the specified filters

        :param filters: The filters to use on the query
        :type filters: dict
        :return: The query of the App Engine
        :rtype: ndb.Query
        """
        if filters.has_key("discipline"):
            disciplines = filters.pop("discipline")
            if not isinstance(disciplines, list):
                disciplines = [disciplines]
            filters['key'] = []
            disciplines_keys = []
            for discipline in disciplines:
                discipline_key = ndb.Key(Discipline, discipline)
                disciplines_keys.append(discipline_key)
            results = Discipline.query(Discipline.key.IN(disciplines_keys))
            for result in results.iter():
                filters["key"].extend(map(lambda key: key.id(), result.teams))
        return super(TeamsRepository, self).find_by(filters)



class TeachersRepository(NDBRepository):
    __model__ = Teacher


class SchedulesRepository(NDBRepository):
    __model__ = Schedule
