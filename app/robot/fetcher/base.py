__author__ = 'fernando'

class BaseFetcher(object):
    def fetch(self, data=None, page_number=1):
        """
        Fetch page with the passed in parameters in the POST request, such as campi and semesters
        available to search.

        :param data: The data to send to the page, or None to make a GET request
        :type data: dict|None
        :param page_number: The page number to access
        :type page_number: int
        """
        raise NotImplemented

    def fetch_campi(self):
        """
        Fetch all campus available to search

        :return: The campi fetched from the page
        :rtype: list of app.robot.value_objects.Campus
        """
        raise NotImplemented

    def fetch_semesters(self):
        """
        Fetch all semesters available to search

        :return: The semesters fetched from the page
        :rtype: list of app.robot.value_objects.Semester
        """
        raise NotImplemented

    def fetch_teams(self):
        """
        Fetch all the teams available on a page

        :return: The teams found on the page
        :rtype: list of Team
        """
        raise NotImplemented

    def has_next_page(self):
        raise NotImplemented