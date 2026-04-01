"""Scrambled letters text output question module"""

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question

from src.constants.selectors import SELECTORS
from src.utils.lists import _m


class ScrambledLettersQuestion(Question):
    """Scrambled letters text output question"""

    def as_text(self):
        self.question_str = f"{self.element.text} are the letters you can use, you NEED to use every letters"
        return self.question_str

    def get_correct_answer(self):
        result = super().get_correct_answer()
        if result:
            # Convert the answer word to a list of individual characters
            word = result[0]
            return list(word.split(" ")[-1]) if " " in word else list(word)
        return result

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
        try:
            if len(values[0]) > 1:
                values = list(values[0])
        except IndexError:
            values = []

        values = _m(lambda l: l.upper(), values)

        for value in values:
            try:
                options = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
                clicked = False
                for option in options:
                    if option.text.strip().upper() == value.upper():
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

        return self.submit_and_check_correct_answer(values)
