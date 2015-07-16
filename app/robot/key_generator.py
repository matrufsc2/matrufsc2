import hashlib

__author__ = 'fernando'

class KeyGenerator(object):
    def generate_semester_key(self, semester):
        """
        Generate the semester key

        :param semester: The semester in which the key is based on
        :return: The key of the semester
        :rtype: str
        """
        key = "%(id)s-%(name)s" % {
            "id": semester.id,
            "name": semester.name
        }
        key = "matrufsc2-semester-%s" % hashlib.sha1(key).hexdigest()
        return key


    def generate_campus_key(self, campus, semester):
        """
        Generate the campus key

        :param campus: The campus in which the key is based on
        :param semester: The semester in which the key is based on
        :return: The key of the campus
        :rtype: str
        """
        key = "%(semester_id)s-%(semester_name)s-%(id)s-%(name)s" % {
            "id": campus.id,
            "semester_id": semester.id,
            "semester_name": semester.name,
            "name": campus.name
        }
        key = "matrufsc2-campus-%s" % hashlib.sha1(key).hexdigest()
        return key

    def generate_schedule_key(self, schedule):
        """
        Gets a schedule key to use to save cache and other nice things

        :param schedule: The schedule to base the key on
        :return: The key of the schedule
        ;rtype: str
        """
        key = "%(hourStart)d-%(minuteStart)d-%(numberOfLessons)d-%(dayOfWeek)d-%(room)s" % {
            "hourStart": schedule.hourStart,
            "minuteStart": schedule.minuteStart,
            "numberOfLessons": schedule.numberOfLessons,
            "dayOfWeek": schedule.dayOfWeek,
            "room": schedule.room
        }
        key = "matrufsc2-schedule-%s" % hashlib.sha1(key).hexdigest()
        return key

    def generate_teacher_key(self, teacher):
        """
        Gets a teacher key to use to save cache and other nice things

        :param teacher: The teacher to base the key on
        :return: The key of the teacher
        ;rtype: str
        """
        key = "%(teacher_name)s" % {
            "teacher_name": teacher.name
        }
        key = "matrufsc2-teacher-%s" % hashlib.sha1(key).hexdigest()
        return key

    def generate_discipline_key(self, discipline, campus, semester):
        """
        Gets a discipline key to use to save the cache and other nice things

        :param discipline: The discipline to base the key on
        :param campus: The campus to base the key on
        :param semester: The semester to base the key on
        :return: The key of the discipline
        :rtype: str
        """
        key = '%(semester)s-%(campus)s-%(discipline_code)s' % {
            "semester": semester.id,
            "campus": campus.id,
            "discipline_code": discipline.code
        }
        key = "matrufsc2-discipline-%s" % hashlib.sha1(key).hexdigest()
        return key

    def generate_team_key(self, team, campus, semester):
        """
        Generate a team key to use with cache and other nice things

        :param team: The team which the key is based on
        :param campus: The campus which the key is based on
        :param semester: The semester which the key is based on
        :return: The key generated for the team
        :rtype: str
        """
        key = '%(semester_id)s-%(campus)s-%(discipline_code)s-%(team_code)s' % {
            "semester_id": semester.id,
            'campus': campus.id,
            'discipline_code': team.discipline.code,
            'team_code': team.code
        }
        key = "matrufsc2-team-%s" % hashlib.sha1(key).hexdigest()
        return key