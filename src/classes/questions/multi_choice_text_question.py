"""Multi choices with text output question module"""
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question
from src.classes.logger import Logger

from src.utils.strings import escape


class MultiChoiceTextQuestion(Question):
    """Multi choices with text output question"""

    def __init__(self, logger: Logger, element: WebElement, output_multiple: bool):
        super().__init__(logger, element)

        self.output_multiple = output_multiple

    def get_correct_answer(self):
        try:
            locator = (
                By.CSS_SELECTOR,
                ".Question__option.Question__option_correct_yes",
            )
            correct_answer = self.element.find_element(*locator)

            return [correct_answer.text]
        except NoSuchElementException:
            return None

    def as_text(self):
        self.question_str = self.element.text
        return self.question_str

    def answer(self, values: str):
        if not self.output_multiple:
            values = values[:1]

        for value in values:
            try:
                xpath = f'//button[contains(@class,"Question__option")]//*[contains(text(), "{escape(value)}")]/..'
                locator = (By.XPATH, xpath)

                button = self.element.find_element(*locator)

                button.click()
                self.logger.debug(f'Selected the "{escape(value)}" choice.')
            except NoSuchElementException:
                msg = "Invalid OpenAI completion answer, taking the 1st answer."
                self.logger.debug(msg)

                xpath = "//button[contains(@class,'Question__option')]"
                button = self.element.find_element(By.XPATH, xpath)
                button.click()

        return self.submit_and_check_correct_answer(values)
