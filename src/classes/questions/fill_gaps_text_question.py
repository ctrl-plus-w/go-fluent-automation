"""Fill gaps text output question module"""
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question
from src.utils.parser import (
    get_fill_gaps_text_question_text_as_text,
    get_green_text_correct_answer,
)


class FillGapsTextQuestion(Question):
    """Fill gaps text output question"""

    def as_text(self):
        html = self.element.get_attribute("outerHTML")
        self.question_str = get_fill_gaps_text_question_text_as_text(html)
        return self.question_str

    def get_correct_answer(self):
        answer = get_green_text_correct_answer(self.element.get_attribute("outerHTML"))

        if answer:
            return [answer]

        self.logger.debug("Did not found a green tag for the correct answer.")
        return None

    def can_answer(self):
        """Check if all the input are filled"""
        return self.get_random_input() is not None

    def get_random_input(self):
        """Get a random option (if no remaining, return None)"""
        try:
            xpath = '//input[contains(@class, "Stem__answer_non-arabic")]'
            inputs = self.element.find_elements(By.XPATH, xpath)

            # Only get inputs that aren't empty
            inputs = list(filter(lambda i: i.get_attribute('value') == '', inputs))

            if len(inputs) == 0:
                return None

            return inputs[0]
        except NoSuchElementException:
            return None

    def select_random_option(self):
        """Select a random option if there's some remaining"""
        text_input = self.get_random_input()
        self.logger.debug("Trying to fill a random option.")

        if text_input:
            self.logger.debug("Filling a random input with 'abcdef'")
            text_input.send_keys("abcdef")
        else:
            self.logger.debug("Did not found any random input.")

    def answer(self, values: list[str]):
        for value in values:
            try:
                locator = (By.XPATH, '//input[contains(@class, "Stem__answer_non-arabic") and .=""]')
                text_input = self.element.find_element(*locator)

                text_input.send_keys(value)
            except NoSuchElementException:
                # If this error happens, it means that OpenAI provided too much responses
                msg = "Invalid OpenAI completion answer, taking the 1st answer."
                self.logger.error(msg)

                break

        while self.can_answer():
            self.select_random_option()

        return self.submit_and_check_correct_answer(values)
