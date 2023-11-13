"""Main"""
import sys
import re

from datetime import datetime

from src.classes.logger import Logger
from src.classes.scraper import Scraper
from src.classes.cli import CLI

from src.utils.fs import create_directory


def main():
    """Main app method"""
    dt_directory = re.sub(r" |:|-", "_", str(datetime.now()).split(".", maxsplit=1)[0])
    logs_directory = f"logs/{dt_directory}"

    create_directory(logs_directory)

    logger = Logger("MAIN", f"{logs_directory}/logs.txt")

    if "--auto-run" in sys.argv:
        scraper = Scraper(logger)

        activities = scraper.retrieve_activities()

        # for activity in activities:
        #     scraper.do_activity(activity)
    else:
        cli = CLI(logger)
        cli.run()

    # SHORT TEXT URL : https://portal.gofluent.com/app/dashboard/atp/vocabulary/81854/85943


if __name__ == "__main__":
    main()
