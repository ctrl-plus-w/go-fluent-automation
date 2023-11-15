"""Fill gaps block output question module"""

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.classes.question import Question

from src.utils.strings import escape
from src.utils.parser import (
    get_fill_gaps_block_question_as_text,
    get_green_text_correct_answer,
)


class FillGapsBlockQuestion(Question):
    """Fill gaps blocks output question"""

    def as_text(self):
        html = self.element.get_attribute("outerHTML")
        self.question_str = get_fill_gaps_block_question_as_text(html)
        return self.question_str

    def get_correct_answer(self):
        content = get_green_text_correct_answer(self.element.get_attribute("outerHTML"))

        if content:
            return content.split(", ")

        return None

    def can_answer(self):
        """Check if all the fill options buttons are filled"""
        for button in self.element.find_elements(By.CSS_SELECTOR, ".Stem__answer"):
            if button.text == "":
                return True

        return False

    def get_random_option(self):
        """Get a random option (if no remaining, return None)"""
        try:
            xpath = '//*[contains(@class,"Question__fill-button") and not(contains(@class, "Question__fill-button_selected_yes"))]'
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
                xpath = f'//button[contains(@class, "Question__fill-button") and contains(text(), "{escape(value)}")]'
                locator = (By.XPATH, xpath)

                button = self.element.find_element(*locator)

                button.click()
            except NoSuchElementException:
                msg = "Invalid OpenAI completion answer, taking the 1st answer."
                self.logger.error(msg)

                self.select_random_option()

        while self.can_answer():
            self.select_random_option()

        return self.submit_and_check_correct_answer(values)
