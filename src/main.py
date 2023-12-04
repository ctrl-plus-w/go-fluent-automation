"""Main"""
import sys
import re
import chalk

from datetime import datetime

from src.classes.logger import Logger
from src.classes.scraper import Scraper
from src.classes.cli import CLI

from src.utils.fs import create_directory


def main():
    """Main app method"""
    dt_directory = re.sub(r"[ :-]", "_", str(datetime.now()).split(".", maxsplit=1)[0])
    logs_directory = f"logs/{dt_directory}"

    create_directory(logs_directory)

    logger = Logger("MAIN", f"{logs_directory}/logs.txt")

    if "--auto-run" in sys.argv:
        param_index = sys.argv.index("--auto-run")

        if len(sys.argv) - 1 <= param_index:
            raise ValueError("Missing --auto-run count property.")

        count = int(sys.argv[param_index + 1])
        logger.info(f"Starting the automaion operations for {count} activities.")

        scraper = Scraper(logger)

        activities = scraper.retrieve_activities(count)

        for i, activity in enumerate(activities):
            logger.info(
                chalk.bold(
                    chalk.cyan(
                        f"\nStarting the activity with url : '{activity.url}' ({i+1}/{len(activities)})"
                    )
                )
            )
            scraper.do_activity(activity)

        scraper.driver.quit()

    else:
        cli = CLI(logger)
        cli.run()


if __name__ == "__main__":
    main()
