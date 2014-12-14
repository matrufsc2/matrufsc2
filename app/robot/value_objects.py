__author__ = 'fernando'


class BaseValueObject(object):
    __slots__ = ["__saved"]

    def __getitem__(self, item):
        raise ReferenceError("Use object.%s to access the value of the attribute" % item)

    def __setattr__(self, key, value):
        if not hasattr(self, "_BaseValueObject__saved"):
            super(BaseValueObject, self).__setattr__("_BaseValueObject__saved", [])
        if hasattr(self, '_BaseValueObject__saved') and key in self.__saved:
            raise RuntimeError("Unable to set attribute '%s' which is already initializated" % key)
        super(BaseValueObject, self).__setattr__(key, value)
        self.__saved.append(key)


class Semester(BaseValueObject):
    __slots__ = ["id", "name"]

    def __init__(self, **kwargs):
        super(Semester, self).__init__()
        self.id = kwargs["id"]
        """ :type: str """
        self.name = kwargs["name"]
        """ :type: str """

    def __getstate__(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.name = state["name"]


class Campus(BaseValueObject):
    __slots__ = ["id", "name"]

    def __init__(self, **kwargs):
        super(Campus, self).__init__()
        self.id = kwargs["id"]
        """ :type: str """
        self.name = kwargs["name"]
        """ :type: str """

    def __getstate__(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def __setstate__(self, state):
        self.id = state["id"]
        self.name = state["name"]


class Teacher(BaseValueObject):
    __slots__ = ["name"]

    def __init__(self, **kwargs):
        super(Teacher, self).__init__()
        self.name = kwargs["name"]
        """ :type: str """

    def __getstate__(self):
        return {
            "name": self.name
        }

    def __setstate__(self, state):
        self.name = state["name"]


class Discipline(BaseValueObject):
    __slots__ = ["code", "name"]

    def __init__(self, **kwargs):
        super(Discipline, self).__init__()
        self.code = kwargs["code"]
        """ :type: str """
        self.name = kwargs["name"]
        """ :type: str """

    def __getstate__(self):
        return {
            "code": self.code,
            "name": self.name
        }

    def __setstate__(self, state):
        self.code = state["code"]
        self.name = state["name"]


class Schedule(BaseValueObject):
    __slots__ = ["dayOfWeek", "hourStart", "minuteStart", "numberOfLessons", "room"]


    def __init__(self, **kwargs):
        super(Schedule, self).__init__()
        self.dayOfWeek = kwargs["dayOfWeek"]
        """ :type: int """
        self.hourStart = kwargs["hourStart"]
        """ :type: int """
        self.minuteStart = kwargs["minuteStart"]
        """ :type: int """
        self.numberOfLessons = kwargs["numberOfLessons"]
        """ :type: int """
        self.room = kwargs["room"]
        """ :type: str """

    def __getstate__(self):
        return {
            "dayOfWeek": self.dayOfWeek,
            "hourStart": self.hourStart,
            "minuteStart": self.minuteStart,
            "numberOfLessons": self.numberOfLessons,
            "room": self.room
        }

    def __setstate__(self, state):
        self.dayOfWeek = state["dayOfWeek"]
        self.hourStart = state["hourStart"]
        self.minuteStart = state["minuteStart"]
        self.numberOfLessons = state["numberOfLessons"]
        self.room = state["room"]


class Team(BaseValueObject):
    __slots__ = ["code", "discipline", "teachers", "vacancies_offered", "vacancies_filled", "schedules"]

    def __init__(self, **kwargs):
        super(Team, self).__init__()
        self.code = kwargs["code"]
        """ :type: str """
        self.discipline = kwargs["discipline"]
        """ :type: app.robot.value_objects.Discipline """
        self.teachers = kwargs["teachers"]
        """ :type: list of app.robot.value_objects.Teacher """
        self.vacancies_offered = kwargs["vacancies_offered"]
        """ :type: int """
        self.vacancies_filled = kwargs["vacancies_filled"]
        """ :type: int """
        self.schedules = kwargs["schedules"]
        """ :type: list of app.robot.value_objects.Schedule """

    def __getstate__(self):
        return {
            "code": self.code,
            "discipline": self.discipline,
            "teachers": self.teachers,
            "vacancies_offered": self.vacancies_offered,
            "vacancies_filled": self.vacancies_filled,
            "schedules": self.schedules
        }

    def __setstate__(self, state):
        self.code = state["code"]
        self.discipline = state["discipline"]
        self.teachers = state["teachers"]
        self.vacancies_offered = state["vacancies_offered"]
        self.vacancies_filled = state["vacancies_filled"]
        self.schedules = state["schedules"]
