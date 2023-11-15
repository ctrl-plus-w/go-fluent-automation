"""Scrambled letters text output question module"""

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.classes.question import Question

from src.utils.lists import _m
from src.utils.strings import escape


class ScrambledLettersQuestion(Question):
    """Scrambled letters text output question"""

    def as_text(self):
        self.question_str = f"{self.element.text} are the letters you can use, you NEED to use every letters"
        return self.question_str

    def get_correct_answer(self):
        try:
            locator = (
                By.CSS_SELECTOR,
                ".Question_type_scrambled-letters__correct-answer-block > div",
            )
            correct_answer = self.element.find_element(*locator)

            return list(correct_answer.text)
        except NoSuchElementException:
            return None

    def get_random_option(self):
        """Get a random option (if no remaining, return None)"""
        try:
            xpath = '//*[contains(@class,"Question_type_scrambled-letters__unselected-box")]//button[contains(@class,"ScrambledLettersOption")]'
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

    def answer(self, values: str):
        if len(values[0]) > 1:
            values = list(values[0])

        values = _m(lambda l: l.upper(), values)

        for value in values:
            try:
                xpath = "".join(
                    [
                        '//*[contains(@class,"Question_type_scrambled-letters__unselected-box")]',
                        f'//button[contains(@class,"ScrambledLettersOption") and (contains(text(), "{escape(value).upper()}") or contains(text(), "{escape(value).lower()}"))]',
                    ]
                )

                locator = (By.XPATH, xpath)
                button = self.element.find_element(*locator)
                button.click()
            except NoSuchElementException:
                msg = "Invalid OpenAI completion answer, taking the 1st answer."
                self.logger.error(msg)

                self.select_random_option()

        while self.get_random_option():
            self.select_random_option()

        return self.submit_and_check_correct_answer(values)
