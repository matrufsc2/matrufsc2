import hashlib
from google.appengine.api import users
from app.json_serializer import JSONSerializable, JSONEncoder
from google.appengine.ext import ndb
from app.cache import lru_cache as cache
import json, logging as _logging

logging = _logging.getLogger("matrufsc2-model")


class Semester(ndb.Model, JSONSerializable):
    __slots__ = ["name", "campi"]
    name = ndb.StringProperty(indexed=False)
    campi = ndb.KeyProperty(kind="Campus", repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Campus(ndb.Model, JSONSerializable):
    __slots__ = ["code", "disciplines"]
    name = ndb.StringProperty(indexed=False)
    disciplines = ndb.KeyProperty(kind="Discipline", repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Discipline(ndb.Model, JSONSerializable):
    __slots__ = ["code", "name", "teams"]
    code = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    teams = ndb.KeyProperty(kind="Team", repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name
        }


class Team(ndb.Model, JSONSerializable):
    __slots__ = ["code", "vacancies_offered", "vacancies_filled", "schedules", "teachers"]
    code = ndb.StringProperty(indexed=False)
    vacancies_offered = ndb.IntegerProperty(indexed=False)
    vacancies_filled = ndb.IntegerProperty(indexed=False)
    schedules = ndb.KeyProperty(kind="Schedule", repeated=True, indexed=False)
    teachers = ndb.KeyProperty(kind="Teacher", repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        schedules = []
        found_schedules = []
        for schedule in self.schedules:
            cache_value = cache.get(schedule.id())
            if cache_value:
                found_schedules.append(cache_value)
            else:
                schedules.append(schedule)
        teachers = []
        found_teachers = []
        for teacher in self.teachers:
            cache_value = cache.get(teacher.id())
            if cache_value:
                found_teachers.append(cache_value)
            else:
                teachers.append(teacher)
        schedules, teachers = (ndb.get_multi_async(schedules, use_cache=False, use_memcache=True),
                               ndb.get_multi_async(teachers, use_cache=False, use_memcache=True))
        for found_schedule in schedules:
            found_schedule = json.loads(json.dumps(found_schedule.get_result(), cls=JSONEncoder))
            if found_schedule:
                cache[found_schedule["id"]] = found_schedule
                found_schedules.append(found_schedule)
            else:
                logging.warning("Not found schedule for team %s. Check manually, please.", self.id)
        for found_teacher in teachers:
            found_teacher = json.loads(json.dumps(found_teacher.get_result(), cls=JSONEncoder))
            if found_teacher:
                cache[found_teacher["id"]] = found_teacher
                found_teachers.append(found_teacher)
            else:
                logging.warning("Not found teacher for team %s. Check manually, please.", self.id)

        return {
            "id": self.id,
            "code": self.code,
            "vacancies_offered": self.vacancies_offered,
            "vacancies_filled": self.vacancies_filled,
            "schedules": found_schedules,
            "teachers": found_teachers
        }


class Teacher(ndb.Model, JSONSerializable):
    __slots__ = ["name"]
    name = ndb.StringProperty(indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Schedule(ndb.Model, JSONSerializable):
    __slots__ = ["hourStart", "minuteStart", "numberOfLessons", "dayOfWeek", "room"]
    hourStart = ndb.IntegerProperty(indexed=False)
    minuteStart = ndb.IntegerProperty(indexed=False)
    numberOfLessons = ndb.IntegerProperty(indexed=False)
    dayOfWeek = ndb.IntegerProperty(indexed=False)
    room = ndb.StringProperty(indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "hourStart": self.hourStart,
            "minuteStart": self.minuteStart,
            "numberOfLessons": self.numberOfLessons,
            "dayOfWeek": self.dayOfWeek,
            "room": self.room
        }


class Plan(ndb.Model, JSONSerializable):
    code = ndb.StringProperty(indexed=False)
    history = ndb.JsonProperty(indexed=False, compressed=True)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        history = self.history
        return {
            "id": self.id,
            "code": self.code,
            "history": history,
            "data": history[0]["data"]
        }

    @staticmethod
    def generate_id_string(code):
        user = users.get_current_user()
        if user:
            user = user.user_id()
        hash_code = "matrufsc2-plan-%s"%hashlib.sha1("-".join([code.encode("utf-8"), str(user)])).hexdigest()
        return hash_code
