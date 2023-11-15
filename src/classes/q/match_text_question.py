"""Match text question module"""
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.common.by import By

from src.classes.question import Question

from src.utils.strings import escape
from src.utils.parser import (
    get_match_text_question_correct_answers,
    get_match_text_question_as_text,
)


class MatchTextQuestion(Question):
    """Match text question"""

    def as_text(self):
        html = self.element.get_attribute("outerHTML")
        self.question_str = get_match_text_question_as_text(html)
        return self.question_str

    def get_correct_answer(self):
        """Get the correct answer (text in green) of the quiz question"""
        html = self.element.get_attribute("outerHTML")
        return get_match_text_question_correct_answers(html)

    def get_random_option(self):
        """Get a random option (if no remaining, return None)"""
        try:
            xpath = '//button[contains(@class,"Question__fill-button") and not(contains(@class,"Question__fill-button_selected_yes"))]'
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

    def answer(self, values: list[str]):
        for value in values:
            try:
                self.logger.debug(f"Retrieving button with value: '{escape(value)}'")
                xpath = f'//button[contains(@class, "Question__fill-button") and not(contains(@class, "Question__fill-button-button_selected_yes")) and contains(text(), "{escape(value)}")]'
                locator = (By.XPATH, xpath)

                button = self.element.find_element(*locator)

                button.click()
            except (NoSuchElementException, InvalidSelectorException):
                msg = "Invalid OpenAI completion answer, taking the 1st answer."
                self.logger.error(msg)

                self.select_random_option()

        while not (self.get_random_option() is None):
            self.select_random_option()

        return self.submit_and_check_correct_answer(values)
