from app.json_serializer import JSONSerializable
from google.appengine.ext import ndb


class Semester(ndb.Model, JSONSerializable):
    name = ndb.StringProperty(indexed=False)

    @property
    def id(self):
        return self.key.id()

    @property
    def campi(self):
        return Campus.query(semester=self.key)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Campus(ndb.Model, JSONSerializable):
    name = ndb.StringProperty(indexed=False)
    semester = ndb.KeyProperty(kind=Semester)

    @property
    def id(self):
        return self.key.id()

    @property
    def disciplines(self):
        return Discipline.query(campus=self.key)


    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Teacher(ndb.Model, JSONSerializable):
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


class Team(ndb.Model, JSONSerializable):
    code = ndb.StringProperty(indexed=False)
    vacancies_offered = ndb.IntegerProperty(indexed=False)
    vacancies_filled = ndb.IntegerProperty(indexed=False)
    schedules = ndb.KeyProperty(kind=Schedule, repeated=True, indexed=False)
    teachers = ndb.KeyProperty(kind=Teacher, repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "vacancies_offered": self.vacancies_offered,
            "vacancies_filled": self.vacancies_filled,
            "schedules": ndb.get_multi(self.schedules),
            "teachers": ndb.get_multi(self.teachers)
        }

class Discipline(ndb.Model, JSONSerializable):
    code = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    campus = ndb.KeyProperty(Campus)
    teams = ndb.KeyProperty(kind=Team, repeated=True, indexed=False)

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name
        }