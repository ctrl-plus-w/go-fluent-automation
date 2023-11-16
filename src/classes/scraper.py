"""Selenimu scrapper"""
import sys

from typing import Tuple, Optional
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import Firefox

from src.classes.activity import Activity
from src.classes.learning import ActivityLearning
from src.classes.solving import ActivitySolving
from src.classes.logger import Logger

from src.utils.parser import get_urls_from_activities_container
from src.utils.lists import _m


from src.constants.credentials import USERNAME, PASSWORD
from src.constants.selectors import SELECTORS


def logged_in(func):
    """Decorator to log in if the user isn't yet"""

    def wrapper(self: "Scraper", *args, **kwargs):
        self.login()
        return func(self, *args, **kwargs)

    return wrapper


class Scraper:
    """Scrapper class"""

    def __init__(self, logger: Logger):
        self.logger = logger

        self.setup_session()

    def wait_for_element(
        self,
        locator: Tuple[str, str],
        message: str,
        timeout: int = 15,
    ):
        """Wait for an element to be visible by the driver"""
        WebDriverWait(self.driver, timeout).until(
            expected_conditions.visibility_of_element_located(locator), message
        )

    def setup_session(self):
        """Initialize the driver"""
        self.logger.info("Initializing the scraper.")

        headless = "--headless" in sys.argv
        prod = "--prod" in sys.argv

        opts = Options()
        servs = Service()

        if prod:
            opts.add_argument("--disable-dev-shm-usage")

        if headless:
            opts.add_argument("--no-sandbox")
            opts.add_argument("--headless")
            opts.headless = True

        self.logger.debug("Creating the driver.")
        self.driver = Firefox(options=opts, service=servs)

        self.driver.maximize_window()

    def is_logged_in(self):
        """Check if the user is logged in to the Go Fluent website"""
        return self.driver.get_cookie("JSESSIONID")

    def are_credentials_invalid(self):
        """Check if the feedback block is shown"""
        try:
            self.wait_for_element(SELECTORS["LOGIN"]["FEEDBACK"], "Invalid", timeout=2)
            return True
        except TimeoutException:
            return False

    def close_modal_if_exists(self):
        """Close the page modal if it exists"""
        try:
            locator = SELECTORS["DASHBOARD"]["MODAL_SKIP"]
            button = self.driver.find_element(*locator)
            button.click()
            self.logger.debug("Closed the modal.")
        except (NoSuchElementException, TimeoutException):
            return

    def login(self, redirect: Optional[str] = None):
        """Log in the user to the GoFluent website"""
        if self.is_logged_in():
            return

        self.logger.info("Logging in to the GoFluent portal.")

        self.driver.get("https://portal.gofluent.com/app/login")

        user_input = self.driver.find_element(*SELECTORS["LOGIN"]["USERNAME_INPUT"])
        password_input = self.driver.find_element(*SELECTORS["LOGIN"]["PASSWORD_INPUT"])
        submit_button = self.driver.find_element(*SELECTORS["LOGIN"]["SUBMIT_BUTTON"])

        # Fill and send the login form
        user_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        submit_button.click()

        if self.are_credentials_invalid():
            self.logger.info("Credentials are invalid.")
            sys.exit()
        else:
            self.logger.error("Credentials are valid.")

        self.close_modal_if_exists()

        # Wait for the next page to load (checking the top left logo)
        self.wait_for_element(SELECTORS["DASHBOARD"]["LOGO"], "User is not logged in.")

        # If the redirected page is not the expected url, redirect
        if redirect and self.driver.current_url != redirect:
            self.driver.get(redirect)

        self.logger.info("Successfully logged in to Go Fluent.")

    @logged_in
    def select_tab(self, tab: str):
        """Switch to the tab (LEARNING_TAB | QUIZ_TAB)"""
        assert tab in ["LEARNING_TAB", "QUIZ_TAB"], "Invalid tab name."

        locator = SELECTORS["NAV"][tab]

        self.wait_for_element(locator, "Page didn't load.", 5)

        button = self.driver.find_element(*locator)
        button.click()

        self.logger.debug(f"Switched to the {tab}.")

    def select_learning_tab(self):
        """Switch to the learning tab"""
        self.select_tab("LEARNING_TAB")

    def select_quiz_tab(self):
        """Switch to the quiz tab"""
        self.select_tab("QUIZ_TAB")

    @logged_in
    def load_activity_page_and_tab(self, activity: Activity, tab: str):
        """Load the activity page from the url and switch to the selected tab"""
        # Navigate to the activity tab if it's not the case yet
        if not self.driver.current_url.startswith(activity.url):
            self.driver.get(activity.url)

        # Wait for the page to load
        locator = SELECTORS["NAV"]["CONTAINER"]
        self.wait_for_element(locator, "Page didn't load.")
        self.logger.debug("Page successfully loaded")

        self.select_tab(tab)

    def is_finished(self):
        """Check if the activity has a finished state"""
        try:
            locator = SELECTORS["QUIZ"]["RETAKE"]
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def get_score(self):
        """Get the quiz score"""
        try:
            value_el = self.driver.find_element(*SELECTORS["QUIZ"]["VALUE"])
            return int(value_el.text[:-1])
        except NoSuchElementException:
            return None

    def retake(self):
        """Retake the quiz"""
        locator = SELECTORS["QUIZ"]["RETAKE"]
        button = self.driver.find_element(*locator)
        button.click()

    @logged_in
    def do_activity(self, activity: Activity):
        """Retrieve the activity data and answer the quiz"""
        learning = ActivityLearning(self.logger, self, activity)
        learning.retrieve_activity_data()

        solving = ActivitySolving(self.logger, self, activity)
        solving.resolve_quiz()

    @logged_in
    def retrieve_activities(self, count=10) -> Activity:
        """Retrieve n activities from the gofluent portal (where n = count)"""
        is_voca = "--vocabulary" in sys.argv
        is_gram = "--grammar" in sys.argv

        if not (is_voca or is_gram):
            raise ValueError(
                "One of the params --grammar or --vocabulary must be specified."
            )

        if is_voca:
            url = "https://portal.gofluent.com/app/dashboard/resources/vocabulary"

        if is_gram:
            url = "https://portal.gofluent.com/app/dashboard/resources/grammar"

        if self.driver.current_url != url:
            self.driver.get(url)

        locator = SELECTORS["VOCABULARY"]["ACTIVITIES_LIST"]
        self.wait_for_element(locator, "Page didn't load.")
        activities_container = self.driver.find_element(*locator)

        html = activities_container.get_attribute("outerHTML")
        activities_urls = get_urls_from_activities_container(html)

        if len(activities_urls) < count:
            script = """
            const element1 = document.querySelector('.browse-all-activities .rcs-inner-container');
            element1.scrollTo({ top: element1.scrollTopMax });
            """

            self.driver.execute_script(script)

            sleep(1)

            return self.retrieve_activities(count)

        self.logger.info(f"Retrieved {len(activities_urls)}. Keeping {count}.")
        return _m(Activity, activities_urls)[:count]
