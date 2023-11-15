"""Short text question module"""
from selenium.webdriver.common.by import By

from src.classes.question import Question

from src.utils.parser import (
    get_green_text_correct_answer,
)


class ShortTextQuestion(Question):
    """Short text question"""

    def as_text(self):
        locator = (By.CSS_SELECTOR, ".Stem__answer-block-text")
        self.question_str = self.element.find_element(*locator).text
        return self.question_str

    def get_correct_answer(self):
        answer = get_green_text_correct_answer(self.element.get_attribute("outerHTML"))

        if answer:
            return [answer]

        self.logger.debug("Did not found a green tag for the correct answer.")
        return None

    def answer(self, values: list[str]):
        value = values[0]

        locator = (By.CSS_SELECTOR, "textarea.Stem__answer_non-arabic")
        text_input = self.element.find_element(*locator)

        text_input.send_keys(value)

        return self.submit_and_check_correct_answer(values)
