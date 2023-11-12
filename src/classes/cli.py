"""Automation CLI"""
import chalk
import validators

from src.classes.activity import Activity
from src.classes.scraper import Scraper
from src.classes.logger import Logger
from src.classes.dotenv import Dotenv


class CLI:
    """Automation CLI"""

    def __init__(self, logger: Logger):
        self.dotenv = Dotenv(".env")
        self.logger = logger

    def run(self):
        """Execute the CLI"""
        print(
            "{} Chargement des {} ⚙️\n".format(
                chalk.bold(chalk.yellow("!")),
                chalk.bold(chalk.blue("variables d'environement")),
            )
        )

        url = input(f"{chalk.bold(chalk.yellow('?'))} Quel est l'URL de l'activité ? ")
        valid = validators.url(url)

        if not valid:
            print(f"{chalk.bold(chalk.yellow('!'))} L'URL est invalide.")
            return

        scraper = Scraper(self.logger)
        activity = Activity(url)

        scraper.do_activity(activity)

        scraper.driver.quit()
