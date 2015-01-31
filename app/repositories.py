from app.exceptions import FieldNotFound
from app.models import Semester, Campus, Discipline, Team, Teacher, Schedule, Plan
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
    __parent__ = None
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
        if len(result) == 1:
            return result[0]
        return ndb.AND(*result)

    @ndb.tasklet
    def find_by(self, filters):
        """
        Created query based on the specified filters

        :param filters: The filters to use on the query
        :type filters: dict
        :return: The results of the query to NDB in App Engine
        :rtype: ndb.Future
        """
        if not filters:
            results = yield self.find_all()
            raise ndb.Return(results)
        if self.__parent__ and filters.has_key(self.__parent__['key']):
            parent_entities = filters.pop(self.__parent__['key'])
            if not isinstance(parent_entities, list):
                parent_entities = [parent_entities]
            old_keys = filters.get('key', None)
            if not old_keys:
                old_keys = []
            if old_keys and not isinstance(old_keys, list):
                old_keys = [old_keys]
            old_keys = set(old_keys) 
            filters['key'] = []
            parent_keys = []
            for parent_entity in parent_entities:
                parent_key = ndb.Key(self.__parent__['model'], parent_entity)
                parent_keys.append(parent_key)
            results = yield ndb.get_multi_async(parent_keys)
            for result in results:
                if not result:
                    continue
                filters["key"].extend(map(lambda key: key.id(), getattr(result, self.__parent__['child_attribute'])))
            if not filters['key']:
                raise ndb.Return([])
            if old_keys:
                filters['key'] = list(set(filters['key']).intersection(old_keys))
        if len(filters) > 1:
            keys = yield self.__get_model__().query(self.__create_filter__(filters)).fetch_async(keys_only=True)
        else:
            # Only parent key was found, search directly on the filters found
            keys = [ndb.Key(self.__get_model__(), key_id) for key_id in filters['key']]
        results = yield ndb.get_multi_async(keys)
        raise ndb.Return(results)

    @ndb.tasklet
    def find_by_id(self, id_value):
        """
        Get an unique model based on the specified id

        :param id_value: The ID of the element to get
        :type id_value: int|string
        :return: The results of the query to NDB in App Engine
        :rtype: ndb.Future
        """
        result = yield self.__get_model__().get_by_id_async(id_value)
        raise ndb.Return(result)

    @ndb.tasklet
    def find_all(self):
        """
        Get all the models on the table

        :return: The results of the query to NDB in App Engine
        :rtype: ndb.Future
        """
        keys = yield self.__get_model__().query().fetch_async(keys_only=True)
        results = yield ndb.get_multi_async(keys)
        raise ndb.Return(results)


class SemesterRepository(NDBRepository):
    __model__ = Semester


class CampusRepository(NDBRepository):
    __model__ = Campus
    __parent__ = {
        "key": "semester",
        "model": Semester,
        "child_attribute": "campi"
    }


class DisciplinesRepository(NDBRepository):
    __model__ = Discipline
    __parent__ = {
        "key": "campus",
        "model": Campus,
        "child_attribute": "disciplines"
    }


class TeamsRepository(NDBRepository):
    __model__ = Team
    __parent__ = {
        "key": "discipline",
        "model": Discipline,
        "child_attribute": "teams"
    }



class TeachersRepository(NDBRepository):
    __model__ = Teacher


class SchedulesRepository(NDBRepository):
    __model__ = Schedule


class PlansRepository(NDBRepository):
    __model__ = Plan