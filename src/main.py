"""Main"""
import argparse
import os

import chalk
import sys
import re

from datetime import datetime
from typing import Optional

from src.classes.logger import Logger

from src.runners.auto_run import AutoRun
from src.runners.simple_run import SimpleRun

from src.utils.fs import create_directory


def get_parser():
    """Generate and return the CLI parser."""
    parser = argparse.ArgumentParser(description="automatically execute some go fluent activities.",
                                     prog="python3 -m src.main")

    # Group1 - Auto-run or simple-run parameters
    group1 = parser.add_mutually_exclusive_group(required=True)

    group1.add_argument('--auto-run', dest="auto_run_count", type=int,
                        help="the amount of activities to do for the month (e.g. only does 2 if you already did 8).")

    group1.add_argument('--simple-run', dest="url",
                        help="the URL of the activity to solve.")

    # Group2 - Vocabulary & Grammar parameters
    group2 = parser.add_mutually_exclusive_group(required='--auto-run' in sys.argv)
    group2.add_argument('--vocabulary', default=True, action='store_true',
                        help="Do the vocabulary activities.")

    group2.add_argument('--grammar', default=False, action="store_false", dest="vocabulary",
                        help="Do the grammar activities")

    # Other parameters
    parser.add_argument('--debug', default=False, required=False,
                        help="Enable the debug mode. Shows more logs messages in the terminal.",
                        action=argparse.BooleanOptionalAction)

    parser.add_argument('--headless', default=True, required=False,
                        help="Run the firefox instance in headless mode (meaning the window won't show).",
                        action=argparse.BooleanOptionalAction)

    parser.add_argument('--profile', default=None, required=False,
                        help="The name of the credentials profile stored in the .env file.")

    return parser


def get_logger(is_debug: bool):
    """Create the logger instance and directory and return it."""
    dt_directory = re.sub(r"[ :-]", "_", str(datetime.now()).split(".", maxsplit=1)[0])
    logs_directory = f"logs/{dt_directory}"

    create_directory(logs_directory)

    return Logger("MAIN", f"{logs_directory}/logs.txt", is_debug)


def get_credentials(logger: Logger, profile: Optional[str]):
    suffix = '' if profile is None else f'__{profile.upper()}'

    username_key = f'GOFLUENT_USERNAME{suffix}'
    password_key = f'GOFLUENT_PASSWORD{suffix}'

    username = os.getenv(username_key)
    password = os.getenv(password_key)

    if username is None or password is None:
        msg = (f"No profile found with the specified profile mathing the following keys : '{username_key}' and"
               f" '{password_key}. Please defined the two keys as strings.")
        logger.error(chalk.bold(chalk.red(msg)))
        sys.exit()

    return username, password


def main():
    """Main method, creating the logs directory for the app instance and running either the CLI or the autorun."""
    parser = get_parser()
    args = parser.parse_args()

    logger = get_logger(args.debug)

    username, password = get_credentials(logger, args.profile)

    try:
        if not (args.auto_run_count is None):
            runner = AutoRun(
                logger=logger,
                auto_run_count=args.auto_run_count,
                is_vocabulary=args.vocabulary,
                is_headless=args.headless,
                username=username,
                password=password
            )
            runner.execute()
        else:
            runner = SimpleRun(
                logger=logger,
                url=args.url,
                is_headless=args.headless,
                username=username,
                password=password
            )
            runner.execute()
    except KeyboardInterrupt:
        logger.error(chalk.bold(chalk.red("The program has been stopped by the keyboard.")))
        return


if __name__ == "__main__":
    main()
