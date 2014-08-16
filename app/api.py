from app.repositories import CampusRepository, DisciplinesRepository, TeamsRepository, TeachersRepository, \
    SchedulesRepository, SemesterRepository

__author__ = 'fernando'


def getCampi(filters):
    repository = CampusRepository()
    if filters:
        return repository.findBy(filters)
    return repository.findAll()


def getCampus(idValue):
    repository = CampusRepository()
    return repository.findByID(idValue)


def getSemesters(filters):
    repository = SemesterRepository()
    if filters:
        return repository.findBy(filters)
    return repository.findAll()


def getSemester(idValue):
    repository = SemesterRepository()
    return repository.findByID(idValue)


def getDisciplines(filters):
    repository = DisciplinesRepository()
    if filters:
        return repository.findBy(filters)
    return repository.findAll()


def getDiscipline(idValue):
    repository = DisciplinesRepository()
    return repository.findByID(idValue)


def getTeams(filters):
    repository = TeamsRepository()
    if filters:
        return repository.findBy(filters)
    return repository.findAll()


def getTeam(idValue):
    repository = TeamsRepository()
    return repository.findByID(idValue)


def getTeachers(filters):
    repository = TeachersRepository()
    if filters:
        return repository.findBy(filters)
    return repository.findAll()


def getTeacher(idValue):
    repository = TeachersRepository()
    return repository.findByID(idValue)


def getSchedules(filters):
    repository = SchedulesRepository()
    if filters:
        return repository.findBy(filters)
    return repository.findAll()


def getSchedule(idValue):
    repository = SchedulesRepository()
    return repository.findByID(idValue)