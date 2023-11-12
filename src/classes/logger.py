"""Logging module"""
import logging
import sys


class Logger:
    """Logging module"""

    def __init__(self, name: str, filename: str):
        self.name = name
        self.logger = logging.getLogger(name)
        self.filename = filename

        self.setup()

    def info(self, message: str):
        """Log an info message"""
        self.logger.info(message)

    def debug(self, message: str):
        """Log a debug message"""
        self.logger.debug(message)

    def error(self, message: str):
        """Log an error message"""
        self.logger.error(message)

    def setup(self):
        """Setup the logger with the handlers and the formatter"""
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(self.filename)
        file_formatter = logging.Formatter(fmt="%(asctime)s [%(name)s] %(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)

        std_handler = logging.StreamHandler()
        std_formatter = logging.Formatter(fmt="%(message)s")
        std_handler.setFormatter(std_formatter)
        std_handler.setLevel(logging.INFO)

        # if "--debug" in sys.argv:
        #     std_handler.setLevel(logging.INFO)

        handlers = [std_handler, file_handler]

        for handler in handlers:
            self.logger.addHandler(handler)

        self.logger.propagate = False
