from app.json_serializer import JSONSerializable
from google.appengine.ext import ndb


class Semester(ndb.Model, JSONSerializable):
    name = ndb.StringProperty()

    @property
    def id(self):
        return self.key.integer_id()

    @property
    def campi(self):
        return Campus.query(semester=self.key)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Campus(ndb.Model, JSONSerializable):
    name = ndb.StringProperty()
    semester = ndb.KeyProperty(kind=Semester)

    @property
    def id(self):
        return self.key.integer_id()

    @property
    def disciplines(self):
        return Discipline.query(campus=self.key)


    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Discipline(ndb.Model, JSONSerializable):
    code = ndb.StringProperty()
    name = ndb.StringProperty()
    campus = ndb.KeyProperty(Campus)

    @property
    def id(self):
        return self.key.integer_id()

    @property
    def teams(self):
        return Team.query(discipline=self.key)

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name
        }

class Teacher(ndb.Model, JSONSerializable):
    name = ndb.StringProperty()

    @property
    def id(self):
        return self.key.integer_id()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Schedule(ndb.Model, JSONSerializable):
    hourStart = ndb.IntegerProperty()
    minuteStart = ndb.IntegerProperty()
    numberOfLessons = ndb.IntegerProperty()
    dayOfWeek = ndb.IntegerProperty()
    room = ndb.StringProperty()

    @property
    def id(self):
        return self.key.integer_id()

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
    code = ndb.StringProperty()
    discipline = ndb.KeyProperty(kind=Discipline, required=True)
    vacancies_offered = ndb.IntegerProperty(indexed=False)
    vacancies_filled = ndb.IntegerProperty(indexed=False)
    schedules = ndb.KeyProperty(kind=Schedule, repeated=True)
    teachers = ndb.KeyProperty(kind=Teacher, repeated=True)

    @property
    def id(self):
        return self.key.integer_id()

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "discipline": self.discipline.integer_id(),
            "vacancies_offered": self.vacancies_offered,
            "vacancies_filled": self.vacancies_filled,
            "schedules": ndb.get_multi(self.schedules),
            "teachers": ndb.get_multi(self.teachers)
        }