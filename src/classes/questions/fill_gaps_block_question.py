"""Fill gaps block output question module"""

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question

from src.constants.selectors import SELECTORS
from src.utils.strings import escape


class FillGapsBlockQuestion(Question):
    """Fill gaps blocks output question"""

    def as_text(self):
        # Get the stem text and available choices
        stem_text = ""
        try:
            stem = self.element.find_element(*SELECTORS["QUIZ"]["STEM"])
            stem_text = stem.text.strip()
        except NoSuchElementException:
            stem_text = self.element.text

        choices = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
        choices_text = "\n".join([f"- {c.text.strip()}" for c in choices])

        self.question_str = f"{stem_text}\n{choices_text}"
        return self.question_str

    def get_correct_answer(self):
        try:
            items = self.element.find_elements(*SELECTORS["QUIZ"]["CORRECT_ANSWER_LIST"])
            if items:
                return [item.text.strip() for item in items if item.text.strip()]

            title = self.element.find_element(*SELECTORS["QUIZ"]["CORRECT_ANSWER_TITLE"])
            text = title.text.strip()
            if text:
                return text.split(", ")
            return None
        except NoSuchElementException:
            return None

    def can_answer(self):
        """Check if there are empty receiver slots"""
        receivers = self.element.find_elements(*SELECTORS["QUIZ"]["RECEIVER"])
        for receiver in receivers:
            if receiver.text.strip() == "":
                return True
        return False

    def get_random_option(self):
        """Get a random unselected option from the source container"""
        try:
            options = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
            return options[0] if options else None
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
            self.logger.debug("Did not find any random options.")

    def answer(self, values: list[str]):
        for value in values:
            try:
                options = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
                clicked = False
                for option in options:
                    if option.text.strip() == value.strip():
                        option.click()
                        clicked = True
                        break

                if not clicked:
                    self.logger.error(
                        "Invalid OpenAI completion answer, taking the 1st answer."
                    )
                    self.select_random_option()
            except NoSuchElementException:
                self.logger.error(
                    "Invalid OpenAI completion answer, taking the 1st answer."
                )
                self.select_random_option()

        max_attempts = 50
        attempts = 0
        while self.can_answer() and attempts < max_attempts:
            if not self.get_random_option():
                self.logger.info("No source options left but receivers still empty.")
                break
            self.select_random_option()
            attempts += 1

        if attempts >= max_attempts:
            self.logger.info("Reached max attempts in fill gaps block cleanup loop.")

        return self.submit_and_check_correct_answer(values)
