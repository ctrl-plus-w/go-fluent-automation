"""Fill gaps text output question module"""
from selenium.webdriver.common.by import By

from src.classes.question import Question

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

    def answer(self, values: list[str]):
        value = values[0]

        locator = (By.CSS_SELECTOR, "input.Stem__answer_non-arabic")
        text_input = self.element.find_element(*locator)

        text_input.send_keys(value)

        return self.submit_and_check_correct_answer(values)
