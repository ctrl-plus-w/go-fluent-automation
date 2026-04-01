"""Multi choices with text output question module"""
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question
from src.classes.logger import Logger

from src.constants.selectors import SELECTORS


class MultiChoiceTextQuestion(Question):
    """Multi choices with text output question"""

    def get_correct_answer(self):
        result = super().get_correct_answer()
        if result:
            return result

        # Fallback: look for the radio option marked as correct
        try:
            options = self.element.find_elements(*SELECTORS["QUIZ"]["RADIO_OPTION"])
            for option in options:
                classes = option.get_attribute("class") or ""
                if "correctSelected" in classes:
                    return [option.text.strip()]
        except NoSuchElementException:
            pass

        return None

    def as_text(self):
        self.question_str = self.element.text
        return self.question_str

    def answer(self, values: list[str]):
        value = values[0] if values else ""

        try:
            options = self.element.find_elements(*SELECTORS["QUIZ"]["RADIO_OPTION"])

            # Try to find matching option by text
            matched = False
            for option in options:
                if value.strip().lower() in option.text.strip().lower():
                    option.click()
                    self.logger.debug(f'Selected the "{value}" choice.')
                    matched = True
                    break

            if not matched and options:
                self.logger.debug(
                    "Invalid OpenAI completion answer, taking the 1st answer."
                )
                options[0].click()

        except NoSuchElementException:
            self.logger.debug("Could not find radio options.")

        return self.submit_and_check_correct_answer(values)
