"""Selenium scrapper"""

from time import sleep
from typing import Tuple, Optional, Callable

import sys
import chalk

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from src.classes.activity import Activity
from src.classes.learning import ActivityLearning
from src.classes.logger import Logger
from src.classes.solving import ActivitySolving

from src.utils.parser import get_urls_from_activities_container, get_date_from_str
from src.utils.cache import add_to_cache, is_in_cache

from src.constants.selectors import SELECTORS


def logged_in(func):
    """Decorator to log in if the user isn't yet"""

    def wrapper(self: "Scraper", *args, **kwargs):
        self.login()
        return func(self, *args, **kwargs)

    return wrapper


class Scraper:
    """Scrapper class"""

    def __init__(
        self,
        logger: Logger,
        is_headless: bool,
        username: str,
        password: str,
        cache: bool,
        minimum_level: str | None = None,
        maximum_level: str | None = None,
    ):
        self.driver: Optional[Firefox] = None
        self.is_headless = is_headless
        self.username = username
        self.password = password
        self.logger = logger
        self.cache = cache
        self.minimum_level = minimum_level
        self.maximum_level = maximum_level

        self.logged_in = False

        self.setup_session()

    def wait_for_element(
        self,
        locator: Tuple[str, str],
        message: str,
        timeout: int = 15,
        to_be_clickable: bool = False,
    ):
        """Wait for an element to be visible by the driver"""
        fn = (
            expected_conditions.element_to_be_clickable
            if to_be_clickable
            else expected_conditions.visibility_of_element_located
        )

        WebDriverWait(self.driver, timeout).until(fn(locator), message)

    def setup_session(self):
        """Initialize the driver"""
        self.logger.info("Initializing the scraper.")

        options = Options()

        # if prod:
        #     options.add_argument("--disable-dev-shm-usage")

        if self.is_headless:
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.headless = True

        self.logger.debug("Creating the driver.")
        self.driver = Firefox(options=options)

        self.driver.maximize_window()

    def is_logged_in(self):
        """Check if the user is logged in to the Go Fluent website"""
        return self.driver.get_cookie("JSESSIONID")

    def are_credentials_invalid(self):
        """Check if the feedback block is shown"""
        try:
            self.wait_for_element(
                SELECTORS["MICROSOFT"]["FEEDBACK"], "Invalid", timeout=2
            )
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

        # when using --simple-run JSESSIONID can't be found
        # so added logged_in attribute to keep track of whether or not
        # we completed the login process
        if self.is_logged_in() or self.logged_in:
            return

        self.logger.info("Logging in to the GoFluent portal.")

        self.driver.get("https://portal.gofluent.com/login/samlconnector")

        # enter the domain
        domain_input = self.driver.find_element(*SELECTORS["LOGIN"]["DOMAIN"])
        submit_button = self.driver.find_element(*SELECTORS["LOGIN"]["SUBMIT_BUTTON"])

        domain_input.send_keys("esaip")
        submit_button.click()

        # redirecting, wait for it to complete
        self.wait_for_element(
            SELECTORS["MICROSOFT"]["USERNAME_INPUT"],
            "'Username' redirection did not work",
        )

        # user input
        user_input = self.driver.find_element(*SELECTORS["MICROSOFT"]["USERNAME_INPUT"])
        submit_button = self.driver.find_element(
            *SELECTORS["MICROSOFT"]["SUBMIT_BUTTON"]
        )

        user_input.send_keys(self.username)
        submit_button.click()

        # redirecting, wait for it to complete
        self.wait_for_element(
            SELECTORS["MICROSOFT"]["PASSWORD_INPUT"],
            "'Password' redirection did not work",
        )

        # enter the password
        password_input = self.driver.find_element(
            *SELECTORS["MICROSOFT"]["PASSWORD_INPUT"]
        )
        submit_button = self.driver.find_element(
            *SELECTORS["MICROSOFT"]["SUBMIT_BUTTON"]
        )

        password_input.send_keys(self.password)
        submit_button.click()

        if self.are_credentials_invalid():
            self.logger.info("Credentials are invalid.")
            sys.exit()
        else:
            self.logger.error("Credentials are valid.")

        # redirecting, wait for it to complete
        self.wait_for_element(
            SELECTORS["MICROSOFT"]["SUBMIT_BUTTON"],
            'Could not find the "Stay signed In?" submit button.',
        )

        # click the "stay signed in" button
        submit_button = self.driver.find_element(
            *SELECTORS["MICROSOFT"]["SUBMIT_BUTTON"]
        )
        submit_button.click()

        # wait for dashboard to appear
        self.wait_for_element(
            SELECTORS["DASHBOARD"]["LOGO"],
            "'Password' redirection did not work",
        )

        self.logger.info("Successfully logged in to Go Fluent.")
        self.logged_in = True

    @logged_in
    def select_tab(self, tab: str):
        """Switch to the tab (LEARNING_TAB | QUIZ_TAB)"""
        assert tab in ["LEARNING_TAB", "QUIZ_TAB"], "Invalid tab name."

        locator = SELECTORS["NAV"][tab]

        self.wait_for_element(
            locator, "Page didn't load. (didn't found the nav tab)", 5
        )

        button = self.driver.find_element(*locator)
        button.click()

        self.logger.debug(f"Switched to the {tab}.")

    @logged_in
    def load_activity_page_and_tab(self, activity: Activity, tab: str):
        """Load the activity page from the url and switch to the selected tab"""
        # Navigate to the activity tab if it's not the case yet
        if not self.driver.current_url.startswith(activity.url):
            self.driver.get(activity.url)

        # Wait for the page to load
        locator = SELECTORS["NAV"]["CONTAINER"]
        self.wait_for_element(
            locator, "Page didn't load. (didn't found the navs container)"
        )
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

    def get_next_page_button(self):
        """Retrieve the pagination next page button"""
        locator = SELECTORS["TRAINING"]["PAGINATION"]
        pagination = self.driver.find_element(*locator)

        locator = SELECTORS["TRAINING"]["PAGINATION_ITEM"]
        button = pagination.find_elements(*locator)[-1]

        return button

    def can_next_page(self):
        """Retrieve whether the button of the pagination is disabled or not"""
        try:
            button = self.get_next_page_button()
            return button.get_attribute("disabled") is None
        except NoSuchElementException:
            return False

    def retrieve_activities_from_block(self, block: WebElement):
        """Retrieve the activities from a block (training page)"""
        locator = SELECTORS["TRAINING"]["BLOCK_DATE"]
        date_el = block.find_element(*locator)

        locator = SELECTORS["TRAINING"]["BLOCK_CARD"]
        block_cards = block.find_elements(*locator)

        date = get_date_from_str(date_el.text)

        activities = []

        for block_card in block_cards:
            locator = SELECTORS["TRAINING"]["BLOCK_CARD_LINK"]
            url = f"https://esaip.gofluent.com{block_card.find_element(*locator).get_attribute('href')}"
            activities.append(Activity(url, date))

        return activities

    @logged_in
    def retrieved_done_activities(self):
        """Retrieve the list of all the done activities"""
        url = "https://esaip.gofluent.com/app/training"
        if self.driver.current_url != url:
            self.driver.get(url)

        locator = SELECTORS["TRAINING"]["CONTAINER"]
        self.wait_for_element(
            locator, "Page didn't load. (didn't found the training container)"
        )

        activities = []

        while self.can_next_page():
            locator = SELECTORS["TRAINING"]["BLOCK_CARD_BLOCK"]
            blocks = self.driver.find_elements(*locator)

            for block in blocks:
                _activities = self.retrieve_activities_from_block(block)
                activities += _activities

            button = self.get_next_page_button()
            # Do not use the selenium `Element.click()` method (doesn't work)
            self.driver.execute_script("arguments[0].click();", button)

        return activities

    @logged_in
    def try_solving_and_set_validity(self, activity: Activity):
        """
        Check if activity validity (trying to load the activity data, if an error is throw, the activity isn't valid)
        """
        try:
            msg = f"\nStarting the activity with url : '{activity.url}'"
            self.logger.info(chalk.bold(chalk.cyan(msg)))

            learning = ActivityLearning(self.logger, self, activity)
            learning.retrieve_activity_data()

            solving = ActivitySolving(self.logger, self, activity)
            activities_done_count = solving.resolve_quiz()

            activity.valid = True if activities_done_count > 0 else False
        except Exception as e:
            self.logger.error(str(e))
            activity.valid = False

        msg = "Activity already done." if not activity.valid else "Activity done !"
        self.logger.info(chalk.bold(chalk.red(msg)))

        if self.cache:
            add_to_cache([activity.url])

        return activity.valid

    @logged_in
    def retrieve_and_do_activities(
        self,
        is_vocabulary: bool,
        count=10,
        cached_activities: list[Activity] = [],
        scroll_count=1,
    ):
        """Retrieve n activities from the go-fluent portal (where n = count)"""
        url = ""

        if is_vocabulary:
            url = "https://esaip.gofluent.com/app/dashboard/resources/vocabulary"
        else:
            url = "https://esaip.gofluent.com/app/dashboard/resources/grammar"

        if self.driver.current_url != url:
            self.driver.get(url)

        locator = SELECTORS["VOCABULARY"]["ACTIVITIES_LIST"]
        self.wait_for_element(
            locator, "Page didn't load. (didn't found the activities list container)"
        )
        activities_container = self.driver.find_element(*locator)

        html = activities_container.get_attribute("outerHTML")
        cached_activities_url = list(
            map(lambda activity1: activity1.url, cached_activities)
        )

        activities_urls = get_urls_from_activities_container(html, self.minimum_level, self.maximum_level)
        activities_urls = list(
            filter(
                lambda url1: not (url1 in cached_activities_url)
                and (not self.cache or not is_in_cache(url1)),
                activities_urls,
            )
        )

        activities = list(map(lambda url1: Activity(url1), activities_urls))
        done_activities = []

        for activity in activities:
            self.try_solving_and_set_validity(activity)
            done_activities.append(activity)

            done_valid_activities_count = len(
                list(
                    filter(
                        lambda activity1: activity1.valid,
                        done_activities + cached_activities,
                    )
                )
            )

            msg = f"Done {done_valid_activities_count}/{count} activities."
            self.logger.info(chalk.bold(chalk.green(msg)))

            if done_valid_activities_count >= count:
                return

        script = """
        const element1 = document.querySelector('.browse-all-activities .rcs-inner-container');
        element1.scrollTo({ top: element1.scrollTopMax });
        """

        for _ in range(scroll_count):
            self.driver.execute_script(script)
            sleep(0.2)

        sleep(0.8)

        return self.retrieve_and_do_activities(
            is_vocabulary,
            count,
            activities,
            scroll_count + 1,
        )
