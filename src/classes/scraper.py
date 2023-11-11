"""Selenimu scrapper"""
import sys

from logging import Logger
from typing import Tuple, Optional

# from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import Firefox

from src.classes.activity import Activity
from src.classes.learning import ActivityLearning
from src.classes.solving import ActivitySolving


from src.constants.credentials import USERNAME, PASSWORD
from src.constants.selectors import SELECTORS


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

    # def wait_and_find_element(self, locator: Tuple[str, str]):
    #     """Wait for the element to be visible on the page and the return the element itself"""
    #     self.wait_for_element(locator, f"Did not found the element {locator}.")
    #     return self.driver.find_element(*locator)

    def setup_session(self):
        """Initialize the driver"""
        self.logger.info("Setting up the session")
        headless = len(sys.argv) > 1 and "--headless" in sys.argv

        opts = Options()
        servs = Service()

        if headless:
            opts.add_argument("--no-sandbox")
            opts.add_argument("--headless")
            opts.headless = True

        self.logger.info("Creating the driver.")
        self.driver = Firefox(options=opts, service=servs)

        self.driver.maximize_window()

    def is_logged_in(self):
        """Check if the user is logged in to the Go Fluent website"""
        return self.driver.get_cookie("JSESSIONID")

    def login(self, redirect: Optional[str] = None):
        """Log in the user to the GoFluent website"""
        if self.is_logged_in():
            return

        self.logger.info("Logging in the user")

        self.driver.get("https://portal.gofluent.com/app/login")

        user_input = self.driver.find_element(*SELECTORS["LOGIN"]["USERNAME_INPUT"])
        password_input = self.driver.find_element(*SELECTORS["LOGIN"]["PASSWORD_INPUT"])
        submit_button = self.driver.find_element(*SELECTORS["LOGIN"]["SUBMIT_BUTTON"])

        # Fill and send the login form
        user_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        submit_button.click()

        # Wait for the next page to load (checking the top left logo)
        self.wait_for_element(SELECTORS["DASHBOARD"]["LOGO"], "User is not logged in.")

        # If the redirected page is not the expected url, redirect
        if redirect and self.driver.current_url != redirect:
            self.driver.get(redirect)

        self.logger.info("Successfully logged in to Go Fluent.")

    @staticmethod
    def logged_in(func):
        """Decorator to log in if the user isn't yet"""

        def wrapper(self: "Scraper", *args, **kwargs):
            self.login()
            return func(self, *args, **kwargs)

        return wrapper

    @logged_in
    def select_tab(self, tab: str):
        """Switch to the tab (LEARNING_TAB | QUIZ_TAB)"""
        assert tab in ["LEARNING_TAB", "QUIZ_TAB"], "Invalid tab name."

        locator = SELECTORS["NAV"][tab]

        self.wait_for_element(locator, "Page didn't load.", 5)

        button = self.driver.find_element(*locator)
        button.click()

        self.logger.info(f"Switched to the {tab}.")

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
        self.logger.info("Page successfully loaded")

        self.select_tab(tab)

    @logged_in
    def do_activity(self, activity: Activity):
        """Retrieve the activity data and answer the quiz"""
        learning = ActivityLearning(self.logger, self, activity)
        learning.retrieve_activity_data()

        solving = ActivitySolving(self.logger, self, activity)
        solving.resolve_quiz()
