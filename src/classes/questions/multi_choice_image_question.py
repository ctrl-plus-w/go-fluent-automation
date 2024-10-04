"""Multi choices with image output question module"""
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question
from src.classes.logger import Logger

from src.utils.strings import escape


class MultiChoiceImageQuestion(Question):
    """Multi choices with image output question"""

    def __init__(self, logger: Logger, q_type: str, element: WebElement):
        super().__init__(logger, q_type, element)

        self.skip_completion = True

    def get_correct_answer(self):
        try:
            locator = (
                By.CSS_SELECTOR,
                ".Question__option.Question__option_correct_yes img",
            )
            correct_answer = self.element.find_element(*locator)
            src = correct_answer.get_attribute("src")

            basepath = "https://esaip.gofluent.com"

            if src.startswith(basepath):
                return [src[len(basepath) :]]

            return [src]

        except NoSuchElementException:
            return None

    def as_text(self):
        self.question_str = self.element.text
        return self.question_str

    def get_random_option(self):
        """Get a random option (if no remaining, return None)"""
        try:
            xpath = '//*[contains(@class,"Question__options")]//button[contains(@class,"Question__option")]'
            return self.element.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    def select_random_option(self):
        """Select a random option if there's some remaining"""
        option = self.get_random_option()
        self.logger.debug("Trying to select a random option.")

        if option:
            self.logger.debug("Selecting a random option.")
            option.click()
        else:
            self.logger.debug("Did not found any random options.")

    def answer(self, values: str):
        value = values[0]

        if value == "SKIP":
            self.select_random_option()
        else:
            xpath = f'//button[contains(@class,"Question__option")]//*[contains(@src, "{value}")]/..'
            locator = (By.XPATH, xpath)

            button = self.element.find_element(*locator)

            button.click()
            self.logger.debug(f'Selected the "{escape(value)}" choice.')

        return self.submit_and_check_correct_answer(values)
