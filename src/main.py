"""Main"""
import argparse
import chalk
import sys
import re

from datetime import datetime

from src.classes.logger import Logger

from src.runners.auto_run import AutoRun
from src.runners.simple_run import SimpleRun

from src.utils.fs import create_directory


def get_parser():
    """Generate and return the CLI parser."""
    parser = argparse.ArgumentParser(description="automatically execute some go fluent activities.")

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

    return parser


def get_logger(is_debug: bool):
    """Create the logger instance and directory and return it."""
    dt_directory = re.sub(r"[ :-]", "_", str(datetime.now()).split(".", maxsplit=1)[0])
    logs_directory = f"logs/{dt_directory}"

    create_directory(logs_directory)

    return Logger("MAIN", f"{logs_directory}/logs.txt", is_debug)


def main():
    """Main method, creating the logs directory for the app instance and running either the CLI or the autorun."""
    parser = get_parser()
    args = parser.parse_args()

    logger = get_logger(args.debug)

    try:
        if 'auto_run_count' in args:
            runner = AutoRun(
                logger=logger,
                auto_run_count=args.auto_run_count,
                is_vocabulary=args.vocabulary,
                is_headless=args.headless
            )
            runner.execute()
        else:
            runner = SimpleRun(logger=logger, url=args.url, is_headless=args.headless)
            runner.execute()
    except KeyboardInterrupt:
        logger.error(chalk.bold(chalk.red("The program has been stopped by the keyboard.")))
        return


if __name__ == "__main__":
    main()
