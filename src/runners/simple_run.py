import validators
import chalk

from src.classes.activity import Activity
from src.classes.scraper import Scraper
from src.classes.logger import Logger


class SimpleRun:
    def __init__(self, logger: Logger, url: str, is_headless: bool):
        self.logger = logger
        self.is_headless = is_headless
        self.url = url

    def execute(self):
        """Simple-run method, solving one activity from the URL."""
        valid = validators.url(self.url)

        if not valid:
            self.logger.info(f"{chalk.bold(chalk.yellow('!'))} L'URL est invalide.")
            return

        scraper = Scraper(logger=self.logger, is_headless=self.is_headless)
        activity = Activity(self.url)

        scraper.do_activity(activity)

        scraper.driver.quit()
