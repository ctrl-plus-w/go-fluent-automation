"""Scrambled sentences block output question module"""

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question

from src.utils.strings import escape
from src.utils.parser import (
    get_scrambled_sentences_block_question_as_text,
    get_green_text_correct_answer,
    get_scrambled_sentences_block_question_choices,
)


class ScrambledSentencesQuestion(Question):
    """Scrambled sentences block output question"""

    def as_text(self):
        html = self.element.get_attribute("outerHTML")
        self.question_str = get_scrambled_sentences_block_question_as_text(html)
        return self.question_str

    def get_correct_answer(self):
        html = self.element.get_attribute("outerHTML")

        # Retrieve the green text (aka the answer)
        answer = get_green_text_correct_answer(html)

        if not answer:
            return None

        # Get the available choices
        choices = get_scrambled_sentences_block_question_choices(html)

        if len(choices) == 0:
            return None

        result = []

        # Get the right choice one by one
        while len(result) < len(choices):
            correct_choice = None

            for choice in choices:
                if answer.startswith(choice):
                    correct_choice = choice
                    answer = answer[len(choice) :].strip()
                    break

            if not correct_choice:
                self.logger.debug("Did not found any correct choice.")
                return None

            result.append(correct_choice)

        return result

    def get_random_option(self):
        """Get a random option (if no remaining, return None)"""
        try:
            xpath = '//*[contains(@class,"Question_type_scrambled-sentence__unselected-box")]//button[contains(@class,"ScrambledSentenceOption")]'
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
        for value in values:
            try:
                self.logger.debug(f"Retrieving button with value: '{escape(value)}'")
                xpath = "".join(
                    [
                        '//*[contains(@class,"Question_type_scrambled-sentence__unselected-box")]',
                        f'//button[contains(@class,"ScrambledSentenceOption") and contains(text(), "{escape(value)}")]',
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
