"""Scraper handler section for the activity tab"""

from typing import TYPE_CHECKING

from src.classes.activity import Activity
from src.classes.logger import Logger

from src.utils.parser import get_data_from_section

from src.constants.selectors import SELECTORS

if TYPE_CHECKING:
    from src.classes.scraper import Scraper


class ActivityLearning:
    """Scraper handler section for the activity tab"""

    def __init__(self, logger: Logger, scraper: "Scraper", activity: Activity):
        self.scraper = scraper
        self.logger = logger
        self.activity = activity

    def retrieve_activity_data(self):
        """Retrieve the data from the activity"""
        self.logger.info("Retrieving the activity data.")

        self.scraper.load_activity_page_and_tab(self.activity, "LEARNING_TAB")

        # Get the list of the available tabs / steps of the activity
        locator = SELECTORS["ACTIVITY"]["TAB"]
        activity_learning_tabs = self.scraper.driver.find_elements(*locator)

        self.logger.debug("Retrieved the activity learning tabs")

        for i, tab in enumerate(activity_learning_tabs):
            tab.click()

            # When switching the learning tab, wait for the content to load
            section = self.scraper.driver.find_element(
                *SELECTORS["ACTIVITY"]["SECTION"]
            )

            html = section.get_attribute("outerHTML")
            data = get_data_from_section(html)
            self.activity.data.append(data)
            self.logger.debug(f"Successfully loaded the tab n°{i}")
