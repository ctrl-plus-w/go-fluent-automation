"""Logging module"""
import logging


class Logger:
    """Logging module"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)

        self.setup()

    def info(self, message: str):
        """Log an info message"""
        self.logger.info(message)

    def error(self, message: str):
        """Log an error message"""
        self.logger.error(message)

    def setup(self):
        """Setup the logger with the handlers and the formatter"""
        std_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(name)s] %(levelname)s :: %(message)s"
        )

        handlers = [std_handler]

        for handler in handlers:
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.logger.setLevel(logging.DEBUG)

        self.logger.propagate = False
