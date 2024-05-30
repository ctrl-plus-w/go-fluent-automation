import sys

from src.classes.scraper import Scraper
from src.classes.logger import Logger

from src.utils.date import is_current_month_and_year
from src.utils.cache import add_to_cache


class AutoRun:
    def __init__(
        self,
        logger: Logger,
        auto_run_count: int,
        is_vocabulary: bool,
        is_headless: bool,
        username: str,
        password: str,
        cache: bool,
    ):
        self.auto_run_count = auto_run_count
        self.is_vocabulary = is_vocabulary
        self.is_headless = is_headless
        self.username = username
        self.password = password
        self.logger = logger
        self.cache = cache

    def execute(self):
        """Auto-run method, retrieving the auto-run count property from the cli, retrieving the amount of done activities,
        retrieving some activities to do and then solving the activities"""
        scraper = Scraper(
            logger=self.logger,
            is_headless=self.is_headless,
            username=self.username,
            password=self.password,
            cache=self.cache,
        )

        self.logger.info("Retrieving the count of done activities for this month.")

        done_activities = scraper.retrieved_done_activities()

        if self.cache:
            add_to_cache(list(map(lambda act: act.url, done_activities)))

        monthly_done_activities = list(
            filter(
                lambda a: a.date and is_current_month_and_year(a.date), done_activities
            )
        )
        monthly_done_activities_count = len(monthly_done_activities)
        self.logger.info(
            f"You have done {monthly_done_activities_count} activities this month."
        )

        todo_count = max(0, self.auto_run_count - monthly_done_activities_count)
        if todo_count == 0:
            self.logger.error(
                "The count of done activities already satisfies the --auto-run count property."
            )
            scraper.driver.quit()
            sys.exit(1)

        scraper.retrieve_and_do_activities(self.is_vocabulary, todo_count)

        scraper.driver.quit()
