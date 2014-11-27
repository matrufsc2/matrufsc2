from selenium.webdriver.support import expected_conditions
from app.robot.exceptions import UFSCBlockException
from app.robot.fetcher.base import BaseFetcher
import logging, time, re
from app.robot.value_objects import Semester, Campus, Team, Discipline, Teacher, Schedule
from selenium.webdriver.support.select import Select
import os
from selenium.webdriver.support.wait import WebDriverWait
from gaenv_lib.selenium.webdriver.common.by import By

logging = logging.getLogger("SeleniumFetcher")



__author__ = 'fernando'

class SeleniumFetcher(BaseFetcher):
    __slots__ = ["browser", "auth", "waiter", "last_data", "base_url"]

    def __init__(self, browser, auth = None):
        """
        Initializes the robot

        :param browser: The browser to use in the requests
        :type browser: selenium.webdriver.remote.webdriver.WebDriver
        :param auth: The authenticator to use
        :type auth: app.robot.fetcher.auth.BaseAuth.BaseAuth
        """
        self.auth = auth
        self.browser = browser
        self.browser.implicitly_wait(5)
        self.waiter = WebDriverWait(self.browser, 20)
        self.last_data = None
        self.base_url = "http://cagr.sistemas.ufsc.br/modules/comunidade/cadastroTurmas/"
        self.login()

    def wait_loading(self):
        self.waiter.until_not(expected_conditions.visibility_of_element_located((By.ID, "loadingDiv")))

    def login(self):
        """
        Do login in CAGR
        """
        if not self.auth or not self.auth.has_data():
            logging.debug("Not logging in")
            return
        logging.debug("Doing login \o/")
        self.browser.get("https://cagr.sistemas.ufsc.br/modules/aluno")
        form = self.browser.find_element_by_id("fm1")
        """ :type: selenium.webdriver.remote.webdriver.WebElement """
        usernameField = form.find_element_by_css_selector("input[name='username']")
        """ :type: selenium.webdriver.remote.webdriver.WebElement """
        usernameField.send_keys(self.auth.get_username())
        passwordField = form.find_element_by_css_selector("input[name='password']")
        """ :type: selenium.webdriver.remote.webdriver.WebElement """
        passwordField.send_keys(self.auth.get_password())
        submitButton = form.find_element_by_css_selector("button[type='submit']")
        """ :type: selenium.webdriver.remote.webdriver.WebElement """
        submitButton.click()
        self.base_url = "https://cagr.sistemas.ufsc.br/modules/aluno/cadastroTurmas/"

    @property
    def page_number(self):
        try:
            scroller = self.browser.find_element_by_id("formBusca:dataScroller1")
        except:
            return 0
        try:
            page_actual = scroller.find_element_by_class_name("rich-datascr-act")
            """ :type: selenium.webdriver.remote.webdriver.WebElement """
            page_number = int(page_actual.text)
            logging.debug("We're in the page %d", page_number)
            return page_number
        except:
            return 0

    def has_next_page(self):
        logging.debug("Checking if there is a next page..")
        try:
            table = self.browser.find_element_by_id("formBusca:dataScroller1_table")
        except:
            logging.debug("Table not found. I just think that there is no 'next' page :D")
            return False
        columns = table.find_elements_by_tag_name("td")
        """ :type: list of selenium.webdriver.remote.webdriver.WebElement """
        for column in columns:
            onclick = column.get_attribute('onclick')
            if onclick is not None and 'next' in onclick:
                logging.debug("Found 'next' page link in column onclick handler: %s", onclick)
                return True
        logging.debug("Not found 'next' page link in %d columns", len(columns))
        return False

    def next_page(self):
        logging.debug("Checking if there is a next page..")
        table = self.browser.find_element_by_id("formBusca:dataScroller1_table")
        assert table, "Cannot locate table of pages"
        next_page_number = self.page_number + 1
        columns = table.find_elements_by_tag_name("td")
        """ :type: list of selenium.webdriver.remote.webdriver.WebElement """
        for column in columns:
            onclick = column.get_attribute('onclick')
            if onclick is not None and 'next' in onclick:
                column.click()
                self.wait_loading()
                self.waiter.until(lambda driver: self.page_number == next_page_number)
                return
        raise Exception("Not found 'next' page link in %d columns"%len(columns))

    def fetch(self, data=None, page_number=1):
        logging.info("Fetching basic information..")
        if not self.browser.page_source or self.browser.current_url != self.base_url:
            self.browser.get(self.base_url)
            self.last_data = None
        if self.page_number > page_number:
            self.last_data = -1 #Just to resend the page
        assert self.browser.page_source, UFSCBlockException()
        if data != self.last_data:
            name_form = "formBusca"
            form = self.browser.find_element_by_css_selector("form[name='%s']"%name_form)
            assert form, UFSCBlockException()
            for key, value in data.iteritems():
                form_input = form.find_element_by_id(":".join([name_form, key]))
                select = Select(form_input)
                select.select_by_value(value)
            button = form.find_element_by_css_selector("input[type='submit']")
            button.click()
            self.wait_loading()
            time.sleep(2)
            self.last_data = data
        while self.has_next_page() and self.page_number < page_number:
            self.next_page()

    def fetch_campi(self):
        """
        Fetch all campus available to search

        :return: The campi fetched from the page
        :rtype: list of app.robot.value_objects.Campus
        """
        logging.debug("Fetching campi in the page..")
        select = self.browser.find_element_by_id("formBusca:selectCampus")
        assert select, "Element not found in the table"
        return [Campus(**{
                    "id": option.get_attribute("value"),
                    "name": option.text
                }) for option in select.find_elements_by_tag_name("option")]

    def fetch_semesters(self):
        """
        Fetch all semesters available to search

        :return: The semesters fetched from the page
        :rtype: list of app.robot.value_objects.Semester
        """
        logging.debug("Fetching semesters in the page..")
        select = self.browser.find_element_by_id("formBusca:selectSemestre")
        assert select, "Element not found in the table"
        return [Semester(**{
                    "id": option.get_attribute("value"),
                    "name": option.text
                }) for option in select.find_elements_by_tag_name("option")]

    def fetch_teams(self):
        """
        Fetch all the teams available on a page

        :param page: The page to process
        :return: The teams found on the page
        :rtype: list of app.robot.value_objects.Team
        """
        try:
            table = self.browser.find_element_by_css_selector("table[id='formBusca:dataTable']")
        except:
            raise UFSCBlockException()
        tbody = table.find_element_by_tag_name("tbody")
        """ :type: selenium.webdriver.remote.webdriver.WebElement """
        rows = tbody.find_elements_by_tag_name("tr")
        """ :type: list of selenium.webdriver.remote.webdriver.WebElement """
        schedule_re = re.compile(
            "(?P<dayOfWeek>\d)\.(?P<hourStart>\d{2})(?P<minuteStart>\d{2})\-(?P<numberOfLessons>\d) \/ (?P<room>.+)")
        logging.debug("Processing %d rows", len(rows))
        teams = []
        for row in rows:
            columns = row.find_elements_by_tag_name("td")
            """ :type: list of selenium.webdriver.remote.webdriver.WebElement """
            if len(columns) < 14:
                logging.error("Ignoring row with only %d columns", len(columns))
                continue
            team = {
                "code": columns[4].text,
                "discipline": Discipline(
                    code=columns[3].text,
                    name=columns[5].text
                ),
                "teachers": map(
                    lambda teacher_name: Teacher(name=teacher_name),
                    filter(
                        None,
                        map(
                            str.strip,
                            map(
                                str,
                                columns[13].text.encode("ISO-8859-1").split("\n")
                            )
                        )
                    )
                ),
                "vacancies_offered": int(columns[7].text),
                "vacancies_filled": int(columns[8].text),
                "schedules": []
            }
            schedules_rows = filter(None, map(str.strip, map(str, columns[12].text.split("\n"))))
            for schedule_row in schedules_rows:
                match = schedule_re.match(schedule_row)
                if not match:
                    # logging.debug("The following schedule row has not matched: %s", schedule_row)
                    continue
                obj = match.groupdict()
                obj['dayOfWeek'] = int(obj['dayOfWeek'])
                obj['hourStart'] = int(obj['hourStart'])
                obj['minuteStart'] = int(obj['minuteStart'])
                obj['numberOfLessons'] = int(obj['numberOfLessons'])
                team["schedules"].append(Schedule(**obj))
            teams.append(Team(**team))
        return teams