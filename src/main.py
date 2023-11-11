"""Main"""

# from openai import OpenAI

from src.classes.logger import Logger
from src.classes.scraper import Scraper
from src.classes.activity import Activity

# from src.utils.openai import generate_prompt


def main():
    """Main app method"""
    logger = Logger("MAIN")

    # Question_type_match-text
    # url = "https://portal.gofluent.com/app/dashboard/atp/vocabulary/81854/84107"
    #        https://portal.gofluent.com/app/dashboard/atp/vocabulary/81854/85967

    # Question_type_fill-in-the-gaps
    # url = "https://portal.gofluent.com/app/dashboard/atp/vocabulary/81854/86018/"

    url = "https://portal.gofluent.com/app/dashboard/atp/vocabulary/81854/85967"

    activity = Activity(url)

    scraper = Scraper(logger)
    scraper.do_activity(activity)


if __name__ == "__main__":
    main()
