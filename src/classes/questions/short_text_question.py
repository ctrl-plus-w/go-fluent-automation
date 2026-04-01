"""Short text question module"""
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question
from src.constants.selectors import SELECTORS


class ShortTextQuestion(Question):
    """Short text question"""

    def as_text(self):
        # Get the stem text (the question/prompt)
        try:
            stem = self.element.find_element(*SELECTORS["QUIZ"]["STEM"])
            self.question_str = stem.text.strip()
        except NoSuchElementException:
            self.question_str = self.element.text
        return self.question_str

    def answer(self, values: list[str]):
        value = values[0]

        locator = (By.CSS_SELECTOR, "textarea")
        text_input = self.element.find_element(*locator)

        text_input.send_keys(value)

        return self.submit_and_check_correct_answer(values)
