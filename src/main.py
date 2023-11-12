"""Main"""

from src.classes.logger import Logger
from src.classes.cli import CLI


def main():
    """Main app method"""
    logger = Logger("MAIN")

    cli = CLI(logger)
    cli.run()

    # SHORT TEXT URL : https://portal.gofluent.com/app/dashboard/atp/vocabulary/81854/85943


if __name__ == "__main__":
    main()
