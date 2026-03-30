"""Selenium scrapper"""

from time import sleep
from typing import Tuple, Optional, Callable
from urllib.parse import urlparse, urlunparse

import os
import sys
import chalk

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
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
        minimum_level: Optional[str] = None,
        maximum_level: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        self.driver: Optional[Firefox] = None
        self.is_headless = is_headless
        self.username = username
        self.password = password
        self.logger = logger
        self.cache = cache
        self.minimum_level = minimum_level
        self.maximum_level = maximum_level
        self.profile = profile

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

        # Use a persistent profile directory to keep session/cookies across runs
        # Each --profile gets its own session directory to avoid SSO account conflicts
        profile_name = self.profile or "default"
        profile_path = os.path.join(os.getcwd(), ".session", profile_name)
        os.makedirs(profile_path, exist_ok=True)
        options.add_argument("-profile")
        options.add_argument(profile_path)

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

    def _wait_for_dashboard(self, timeout=30):
        """Wait for the GoFluent dashboard to load after login"""
        # Try multiple possible indicators that the dashboard has loaded
        for _ in range(timeout * 2):
            sleep(0.5)
            current_url = self.driver.current_url
            # Check if we're on the dashboard
            if "gofluent.com/app/" in current_url and "samlconnector" not in current_url:
                # Try to find any dashboard element
                try:
                    self.driver.find_element(*SELECTORS["DASHBOARD"]["LOGO"])
                    self.logger.debug("Found dashboard logo.")
                    return
                except NoSuchElementException:
                    pass
                # Alternative: check for any common dashboard element
                try:
                    self.driver.find_element(By.CSS_SELECTOR, "[class*='header']")
                    self.logger.debug("Found header element on dashboard.")
                    return
                except NoSuchElementException:
                    pass
                # If we're on a gofluent app page but can't find specific elements,
                # wait a bit for the page to finish loading
                if any(path in current_url for path in ["/dashboard", "/training", "/app/"]):
                    sleep(2)
                    self.logger.debug(f"On GoFluent app page: {current_url}")
                    return

        raise TimeoutException(f"Dashboard did not load after {timeout}s. URL: {self.driver.current_url}")

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

        # Wait for the login page to load
        self.wait_for_element(
            SELECTORS["LOGIN"]["DOMAIN"],
            "Login page did not load (domain input not found)",
            timeout=20,
        )

        # enter the domain
        domain_input = self.driver.find_element(*SELECTORS["LOGIN"]["DOMAIN"])
        submit_button = self.driver.find_element(*SELECTORS["LOGIN"]["SUBMIT_BUTTON"])

        domain_input.send_keys("esaip")
        sleep(0.5)
        submit_button.click()

        self.logger.debug(f"Clicked submit on login page, current URL: {self.driver.current_url}")

        # Wait for either Microsoft login page OR direct dashboard redirect
        # (SAML SSO may bypass Microsoft login if session is cached)
        for _ in range(60):
            sleep(0.5)
            try:
                current_url = self.driver.current_url
            except Exception:
                continue
            if "login.microsoftonline.com" in current_url:
                break
            if "gofluent.com/app/dashboard" in current_url:
                self.logger.debug("Already redirected to dashboard (SSO session cached).")
                self._wait_for_dashboard()
                self.logger.info("Successfully logged in to Go Fluent.")
                self.logged_in = True
                return
            if "gofluent.com/app/" in current_url and "samlconnector" not in current_url:
                self.logger.debug(f"Redirected to GoFluent app: {current_url}")
                self._wait_for_dashboard()
                self.logger.info("Successfully logged in to Go Fluent.")
                self.logged_in = True
                return

        self.logger.debug(f"On Microsoft login page: {self.driver.current_url}")

        # Microsoft login flow — handle "Pick an account" screen if present
        try:
            other_account = self.driver.find_element(*SELECTORS["MICROSOFT"]["PICK_ACCOUNT_OTHER"])
            if other_account.is_displayed():
                self.logger.debug("Found 'Pick an account' screen, clicking 'Use another account'.")
                other_account.click()
        except NoSuchElementException:
            pass

        self.wait_for_element(
            SELECTORS["MICROSOFT"]["USERNAME_INPUT"],
            "'Username' redirection did not work",
            timeout=15,
        )

        # user input — clear any pre-filled value first
        user_input = self.driver.find_element(*SELECTORS["MICROSOFT"]["USERNAME_INPUT"])
        existing_value = user_input.get_attribute("value")
        if existing_value and existing_value.strip() != self.username:
            self.logger.debug(f"Username field pre-filled with '{existing_value}', clearing.")
            user_input.clear()

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
        self.logger.debug(f"Submitted password. URL: {self.driver.current_url}")

        if self.are_credentials_invalid():
            self.logger.info("Credentials are invalid.")
            sys.exit()
        else:
            self.logger.debug("Credentials are valid.")

        # After password submit, wait for either:
        # 1. "Stay signed in?" prompt (Microsoft)
        # 2. Direct redirect to GoFluent dashboard
        # 3. MFA / other Microsoft page -> wait for user to complete manually
        mfa_logged = False
        for _ in range(240):  # Up to 120 seconds for MFA
            sleep(0.5)
            try:
                current_url = self.driver.current_url
            except Exception:
                # Browser window may be temporarily unavailable during redirects
                continue

            # Already redirected to GoFluent
            if "gofluent.com/app/" in current_url:
                self.logger.debug(f"Redirected to GoFluent: {current_url}")
                break

            # Check for "Stay signed in?" prompt (try multiple detection methods)
            try:
                submit_btn = self.driver.find_element(
                    *SELECTORS["MICROSOFT"]["SUBMIT_BUTTON"]
                )
                if submit_btn.is_displayed():
                    # Verify we're on the "Stay signed in?" page (not the password page)
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    if any(t in page_text.lower() for t in ["stay signed in", "rester connecté", "remain signed in"]):
                        self.logger.debug("Found 'Stay signed in?' prompt.")
                        submit_btn.click()
                        self.logger.debug("Clicked 'Yes' button on 'Stay signed in' page.")
                        break
            except NoSuchElementException:
                pass

            # If still on Microsoft login, MFA might be required
            if "login.microsoftonline.com" in current_url and not mfa_logged:
                self.logger.info(
                    chalk.yellow("Waiting for MFA / 2FA approval (complete it in the browser)...")
                )
                mfa_logged = True

        self.logger.debug(f"After post-password wait. URL: {self.driver.current_url}")

        # wait for dashboard to appear
        self._wait_for_dashboard(timeout=60)

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

        # Dismiss any modal backdrop that might be covering the page
        self.close_modal_if_exists()
        try:
            backdrop = self.driver.find_element(
                By.CSS_SELECTOR, ".MuiBackdrop-root"
            )
            self.driver.execute_script("arguments[0].click()", backdrop)
            sleep(1)
        except NoSuchElementException:
            pass

        button = self.driver.find_element(*locator)
        try:
            button.click()
        except Exception:
            # If still intercepted, use JavaScript click as fallback
            self.driver.execute_script("arguments[0].click()", button)

        self.logger.debug(f"Switched to the {tab}.")

    def _rewrite_url_domain(self, url: str) -> str:
        """Rewrite a GoFluent URL to use the same domain as the current session.

        After SSO login the browser lands on e.g. esaip.gofluent.com, but
        user-supplied URLs may use portal.gofluent.com which doesn't share
        the session cookie.
        """
        current = urlparse(self.driver.current_url)
        target = urlparse(url)
        if current.netloc and current.netloc != target.netloc and "gofluent.com" in target.netloc:
            rewritten = urlunparse(target._replace(scheme=current.scheme, netloc=current.netloc))
            self.logger.debug(f"Rewrote URL domain: {target.netloc} → {current.netloc}")
            return rewritten
        return url

    @logged_in
    def load_activity_page_and_tab(self, activity: Activity, tab: str):
        """Load the activity page from the url and switch to the selected tab"""
        url = self._rewrite_url_domain(activity.url)

        # Navigate to the activity tab if it's not the case yet
        if not self.driver.current_url.startswith(url):
            self.logger.debug(f"Navigating to activity URL: {url}")
            self.driver.get(url)
            self.logger.debug(f"After navigation, URL is: {self.driver.current_url}")

        # Wait for the page to load
        locator = SELECTORS["NAV"]["CONTAINER"]
        try:
            self.wait_for_element(
                locator, "Page didn't load. (didn't found the navs container)",
                timeout=30,
            )
        except TimeoutException:
            self.logger.error(f"Tabs not found. Current URL: {self.driver.current_url}")
            raise
        self.logger.debug("Page successfully loaded")

        self.select_tab(tab)

    def is_finished(self):
        """Check if the activity has a finished state"""
        try:
            locator = SELECTORS["QUIZ"]["RETAKE"]
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            pass
        # Fallback: check for the end page container
        try:
            locator = SELECTORS["QUIZ"]["END_PAGE"]
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def get_score(self):
        """Get the quiz score (percentage) from the end page.

        The selector matches multiple elements (container, labels, values).
        We look for the one whose text ends with '%' (e.g. '50%').
        """
        try:
            elements = self.driver.find_elements(*SELECTORS["QUIZ"]["VALUE"])
            for el in elements:
                text = el.text.strip()
                # Look for a short string like "83%" — not the container
                # which includes all text ("Résultat\n5 / 6\nPrécision\n83%")
                if text.endswith("%") and "\n" not in text:
                    try:
                        return int(text[:-1])
                    except ValueError:
                        continue
            return None
        except NoSuchElementException:
            return None

    def retake(self):
        """Retake the quiz"""
        locator = SELECTORS["QUIZ"]["RETAKE"]
        button = self.driver.find_element(*locator)
        button.click()
        sleep(2)  # Wait for page transition after retake

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

        if self.cache and activity.valid:
            add_to_cache([activity.url])

        return activity.valid

    @logged_in
    def retrieve_and_do_activities(
        self,
        is_vocabulary: bool,
        count=10,
        cached_activities: list[Activity] = [],
        scroll_count=1,
        max_scroll_rounds=30,
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

        activities_urls = get_urls_from_activities_container(
            html, self.minimum_level, self.maximum_level
        )
        self.logger.debug(f"Found {len(activities_urls)} total activity URLs on page.")

        activities_urls = list(
            filter(
                lambda url1: not (url1 in cached_activities_url)
                and (not self.cache or not is_in_cache(url1)),
                activities_urls,
            )
        )

        self.logger.debug(f"Found {len(activities_urls)} new (non-cached) activity URLs.")

        # If no new activities found after scrolling, stop recursing
        if not activities_urls:
            if scroll_count >= max_scroll_rounds:
                self.logger.info(
                    chalk.yellow(f"Reached max scroll rounds ({max_scroll_rounds}), stopping.")
                )
                return

            self.logger.debug(f"No new activities found, scrolling (round {scroll_count})...")
        else:
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

            cached_activities = done_activities + cached_activities

        # Scroll to load more activities
        script = """
        const container = document.querySelector('.browse-all-activities__list');
        if (container) {
            container.scrollTop = container.scrollHeight;
            return 'scrolled-list';
        }
        const rcsContainer = document.querySelector('.browse-all-activities .rcs-inner-container');
        if (rcsContainer) {
            rcsContainer.scrollTop = rcsContainer.scrollHeight;
            return 'scrolled-rcs';
        }
        // Fallback: scroll the page itself
        window.scrollTo(0, document.body.scrollHeight);
        return 'scrolled-window';
        """

        for _ in range(scroll_count):
            result = self.driver.execute_script(script)
            self.logger.debug(f"Scroll result: {result}")
            sleep(0.3)

        sleep(1.0)

        return self.retrieve_and_do_activities(
            is_vocabulary,
            count,
            cached_activities,
            scroll_count + 1,
            max_scroll_rounds,
        )
