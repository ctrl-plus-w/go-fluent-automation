"""Fill gaps text output question module"""
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question

from src.constants.selectors import SELECTORS


class FillGapsTextQuestion(Question):
    """Fill gaps text output question"""

    def as_text(self):
        # Get the stem with blanks represented as text
        try:
            stem = self.element.find_element(*SELECTORS["QUIZ"]["STEM"])
            self.question_str = stem.text.strip()
        except NoSuchElementException:
            self.question_str = self.element.text
        return self.question_str

    def get_empty_input(self):
        """Get an empty text input (if none remaining, return None)"""
        try:
            inputs = self.element.find_elements(By.CSS_SELECTOR, "input[type='text']")

            # Only get inputs that aren't filled
            for inp in inputs:
                if inp.get_attribute("value") == "":
                    return inp

            return None
        except NoSuchElementException:
            return None

    def can_answer(self):
        """Check if there are empty inputs remaining"""
        return self.get_empty_input() is not None

    def select_random_option(self):
        """Fill a random empty input with a placeholder"""
        text_input = self.get_empty_input()
        self.logger.debug("Trying to fill a random option.")

        if text_input:
            self.logger.debug("Filling a random input with 'abcdef'")
            text_input.send_keys("abcdef")
        else:
            self.logger.debug("Did not find any empty input.")

    def answer(self, values: list[str]):
        for value in values:
            text_input = self.get_empty_input()
            if text_input:
                text_input.send_keys(value)
            else:
                self.logger.error(
                    "Invalid OpenAI completion answer, no more empty inputs."
                )
                break

        while self.can_answer():
            self.select_random_option()

        return self.submit_and_check_correct_answer(values)
