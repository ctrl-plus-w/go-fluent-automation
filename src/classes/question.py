"""Activity quiz questions modules"""
import chalk

from logging import Logger

from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from src.utils.lists import _m
from src.utils.parser import (
    get_match_text_question_as_text,
    get_match_text_question_correct_answers,
    get_fill_gaps_text_question_text_as_text,
    get_green_text_correct_answer,
    get_fill_gaps_block_question_as_text,
)

from src.constants.selectors import SELECTORS


class Question:
    """Activity quiz question interface"""

    def __init__(self, logger: Logger, element: WebElement):
        self.logger = logger
        self.element = element
        self.question_str = ""
        self.correct_answer = None

    def get_correct_answer(self):
        """Return the value of the correct answer"""
        return []

    def as_text(self):
        """Return the question as text"""
        return

    def answer(self, _value: str):
        """Answer the value and return the correct answer"""
        return []

    def submit_and_check_correct_answer(self, values: list[str]):
        """Submit the question and check if the returned response is correct"""
        submit_button = self.element.find_element(*SELECTORS["QUIZ"]["SUBMIT"])
        submit_button.click()

        correct_answer = self.get_correct_answer()

        if correct_answer and correct_answer != values:
            self.logger.info(
                chalk.red(f"Wrong answer, the correct answer is '{correct_answer}'.")
            )
        else:
            self.logger.info(chalk.green("Correct answer."))

        return correct_answer or values

    @staticmethod
    def from_element(logger: Logger, element: WebElement):
        """Get the appropriate Question sub-class for the element"""

        curr_classes = element.get_attribute("class").split(" ")

        def has_all_classes(classes: list[str]):
            """Check if the element has all the classes passed"""
            return all(_m(lambda c: c in curr_classes, classes))

        otp_block = "Question_output_text-blocks"
        otp_text = "Question_output_text"
        otp_text_mult = "Question_output_text-multiple"

        if (
            has_all_classes(["Question_type_multiple-choice", otp_text])
            or has_all_classes(["Question_type_multiple-choice", otp_text_mult])
            or has_all_classes(["Question_type_true-or-false", otp_text])
        ):
            m = otp_text_mult in curr_classes
            return MultiChoiceTextQuestion(logger, element, m)

        if has_all_classes(["Question_type_scrambled-letters", otp_text]):
            return ScrambledLettersQuestion(logger, element)

        if has_all_classes(["Question_type_match-text", otp_block]):
            return MatchTextQuestion(logger, element)

        if has_all_classes(["Question_type_fill-in-the-gaps", otp_text]):
            return FillGapsTextQuestion(logger, element)

        if has_all_classes(["Question_type_fill-in-the-gaps", otp_block]):
            return FillGapsBlockQuestion(logger, element)

        return None


class MultiChoiceTextQuestion(Question):
    """Multi choices with text output question"""

    def __init__(self, logger: Logger, element: WebElement, output_multiple: bool):
        super().__init__(logger, element)

        self.output_multiple = output_multiple

    def get_correct_answer(self):
        try:
            locator = (
                By.CSS_SELECTOR,
                ".Question__option.Question__option_correct_yes",
            )
            correct_answer = self.element.find_element(*locator)

            return [correct_answer.text]
        except NoSuchElementException:
            return None

    def as_text(self):
        self.question_str = self.element.text
        return self.question_str

    def answer(self, values: str):
        if not self.output_multiple:
            values = values[:1]

        for value in values:
            try:
                xpath = f'//button[contains(@class,"Question__option")]//*[contains(text(), "{value}")]/..'
                locator = (By.XPATH, xpath)

                button = self.element.find_element(*locator)

                button.click()
                self.logger.info(f'Selected the "{value}" choice.')
            except NoSuchElementException:
                msg = "Invalid OpenAI completion answer, taking the 1st answer."
                self.logger.error(msg)

                xpath = "//button[contains(@class,'Question__option')]"
                button = self.element.find_element(By.XPATH, xpath)
                button.click()

        return self.submit_and_check_correct_answer(values)


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
        self.logger.info("Trying to select a random option.")

        if option:
            self.logger.info("Selecting a random option.")
            option.click()
        else:
            self.logger.info("Did not found any random options.")

    def answer(self, values: str):
        if len(values[0]) > 1:
            values = list(values[0])

        values = _m(lambda l: l.upper(), values)

        for value in values:
            try:
                xpath = "".join(
                    [
                        '//*[contains(@class,"Question_type_scrambled-letters__unselected-box")]',
                        f'//button[contains(@class,"ScrambledLettersOption") and contains(text(), "{value.upper()}")]',
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


class MatchTextQuestion(Question):
    """Match text question"""

    def as_text(self):
        html = self.element.get_attribute("outerHTML")
        self.question_str = get_match_text_question_as_text(html)
        return self.question_str

    def get_correct_answer(self):
        """Get the correct answer (text in green) of the quiz question"""
        html = self.element.get_attribute("outerHTML")
        return get_match_text_question_correct_answers(html)

    def get_random_option(self):
        """Get a random option (if no remaining, return None)"""
        try:
            xpath = '//button[contains(@class,"Question__fill-button") and not(contains(@class,"Question__fill-button_selected_yes"))]'
            return self.element.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

    def select_random_option(self):
        """Select a random option if there's some remaining"""
        option = self.get_random_option()
        self.logger.info("Trying to select a random option.")

        if option:
            self.logger.info("Selecting a random option.")
            option.click()
        else:
            self.logger.info("Did not found any random options.")

    def answer(self, values: list[str]):
        for value in values:
            try:
                self.logger.info(f"Retrieving button with value: '{value}'")
                xpath = f'//button[contains(@class, "Question__fill-button") and not(contains(@class, "Question__fill-button-button_selected_yes")) and contains(text(), "{value}")]'
                locator = (By.XPATH, xpath)

                button = self.element.find_element(*locator)

                button.click()
            except (NoSuchElementException, InvalidSelectorException):
                msg = "Invalid OpenAI completion answer, taking the 1st answer."
                self.logger.error(msg)

                self.select_random_option()

        while not (self.get_random_option() is None):
            self.select_random_option()

        return self.submit_and_check_correct_answer(values)


class FillGapsTextQuestion(Question):
    """Fill gaps text output question"""

    def as_text(self):
        html = self.element.get_attribute("outerHTML")
        self.question_str = get_fill_gaps_text_question_text_as_text(html)
        return self.question_str

    def get_correct_answer(self):
        return [get_green_text_correct_answer(self.element.get_attribute("outerHTML"))]

    def answer(self, values: list[str]):
        value = values[0]

        locator = (By.CSS_SELECTOR, "input.Stem__answer_non-arabic")
        text_input = self.element.find_element(*locator)

        text_input.send_keys(value)

        return self.submit_and_check_correct_answer(values)


class FillGapsBlockQuestion(Question):
    """Fill gaps blocks output question"""

    def as_text(self):
        html = self.element.get_attribute("outerHTML")
        self.question_str = get_fill_gaps_block_question_as_text(html)
        return self.question_str

    def get_correct_answer(self):
        content = get_green_text_correct_answer(self.element.get_attribute("outerHTML"))

        if content:
            return content.split(", ")

    def answer(self, values: list[str]):
        i = 0

        while i < len(values):
            try:
                value = values[i]
                i += 1

                xpath = f'//button[contains(@class, "Question__fill-button") and contains(text(), "{value}")]'
                locator = (By.XPATH, xpath)

                button = self.element.find_element(*locator)

                button.click()
            except NoSuchElementException:
                msg = "Invalid OpenAI completion answer, taking the 1st answer."
                self.logger.error(msg)

                # Try to find an letter in the unselected letters
                try:
                    xpath = '//button[contains(@class,"Question__fill-button")]'
                    button = self.element.find_element(By.XPATH, xpath)
                    button.click()
                except NoSuchElementException:
                    self.logger.info(
                        "Did not found any more unselected letters, stopping the loop"
                    )
                    break

        return self.submit_and_check_correct_answer(values)
