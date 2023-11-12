"""Main"""

# from openai import OpenAI

from src.classes.logger import Logger
from src.classes.scraper import Scraper
from src.classes.activity import Activity


def main():
    """Main app method"""
    logger = Logger("MAIN")

    # SHORT TEXT URL : https://portal.gofluent.com/app/dashboard/atp/vocabulary/81854/85943

    url = "https://portal.gofluent.com/app/dashboard/resources/vocabulary/81854/85894"

    activity = Activity(url)

    scraper = Scraper(logger)
    scraper.do_activity(activity)


if __name__ == "__main__":
    main()
