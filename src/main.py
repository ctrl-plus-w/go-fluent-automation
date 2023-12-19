"""Main"""
import sys
import re
import chalk

from datetime import datetime

from src.classes.logger import Logger
from src.classes.scraper import Scraper
from src.classes.cli import CLI
from src.utils.date import is_current_month

from src.utils.fs import create_directory


def auto_run(logger: Logger):
    param_index = sys.argv.index("--auto-run")

    if len(sys.argv) - 1 <= param_index:
        raise ValueError("Missing --auto-run count property.")

    count = int(sys.argv[param_index + 1])
    logger.info(f"Starting the automation operations for {count} activities.")

    scraper = Scraper(logger)

    logger.info("Retrieving the count of done activities for this month.")
    done_activities = scraper.retrieved_done_activities()
    monthly_done_activities = list(filter(lambda a: a.date and is_current_month(a.date), done_activities))
    monthly_done_activities_count = len(monthly_done_activities)
    logger.info(f"You have done {monthly_done_activities_count} activities this month.")

    todo_count = max(0, count - monthly_done_activities_count)
    if todo_count == 0:
        logger.error("The count of done activities already satisfies the --auto-run count property.")
        scraper.driver.quit()
        sys.exit(1)

    activities = scraper.retrieve_activities(todo_count)

    for i, activity in enumerate(activities):
        msg = f"\nStarting the activity with url : '{activity.url}' ({i + 1}/{len(activities)})"
        logger.info(chalk.bold(chalk.cyan(msg)))
        scraper.do_activity(activity)

    scraper.driver.quit()


def main():
    """Main app method"""
    dt_directory = re.sub(r"[ :-]", "_", str(datetime.now()).split(".", maxsplit=1)[0])
    logs_directory = f"logs/{dt_directory}"

    create_directory(logs_directory)

    logger = Logger("MAIN", f"{logs_directory}/logs.txt")

    if "--auto-run" in sys.argv:
        auto_run(logger)
    else:
        cli = CLI(logger)
        cli.run()


if __name__ == "__main__":
    main()
