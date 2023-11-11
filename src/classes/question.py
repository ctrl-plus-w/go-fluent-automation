"""Activity quiz questions modules"""
from logging import Logger

from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.utils.lists import _m

from src.constants.selectors import SELECTORS


class Question:
    """Activity quiz question interface"""

    def __init__(self, logger: Logger, element: WebElement):
        self.logger = logger
        self.element = element
        self.correct_answer = None

    def get_correct_answer(self):
        """Return the value of the correct answer"""
        return

    def as_text(self):
        """Return the question as text"""
        return

    def answer(self, _value: str):
        """Answer the value and return the correct answer"""
        return

    @staticmethod
    def from_element(logger: Logger, element: WebElement):
        """Get the appropriate Question sub-class for the element"""

        def has_all_classes(classes: list[str]):
            """Check if the element has all the classes passed"""
            curr_classes = element.get_attribute("class").split(" ")
            return all(_m(lambda c: c in curr_classes, classes))

        if has_all_classes(["Question_type_multiple-choice", "Question_output_text"]):
            return MultiChoiceTextQuestion(logger, element)

        if has_all_classes(["Question_type_scrambled-letters", "Question_output_text"]):
            return ScrambledLettersQuestion(logger, element)

        # TODO : Add other questions types

        return None


class MultiChoiceTextQuestion(Question):
    """Multi choices with text output question"""

    def get_correct_answer(self):
        try:
            locator = (
                By.CSS_SELECTOR,
                ".Question__option.Question__option_correct_yes",
            )
            correct_answer = self.element.find_element(*locator)

            return correct_answer.text
        except NoSuchElementException:
            return None

    def as_text(self):
        return self.element.text

    def answer(self, values: str):
        value = values[0]

        try:
            xpath = f'//button[@class="Question__option"]//*[contains(text(), "{value}")]/..'
            locator = (By.XPATH, xpath)

            button = self.element.find_element(*locator)

            button.click()
            self.logger.info(f'Selected the "{value}" choice.')
        except NoSuchElementException:
            msg = "Invalid OpenAI completion answer, taking the 1st answer."
            self.logger.error(msg)

            xpath = "//button[@class='Question__option']"
            button = self.element.find_element(By.XPATH, xpath)
            button.click()

        submit_button = self.element.find_element(*SELECTORS["QUIZ"]["SUBMIT"])
        submit_button.click()

        correct_answer = self.get_correct_answer()

        if correct_answer and correct_answer != value:
            self.logger.info(f"Wrong answer, the correct answer is {correct_answer}.")
        else:
            self.logger.info("OpenAI returned a correct answer.")

        return correct_answer or value


class ScrambledLettersQuestion(Question):
    """Scrambled letters text output question"""

    def as_text(self):
        return f"{self.element.text} are the letters you can use, you NEED to use every letters"

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

    def answer(self, values: str):
        if len(values[0]) > 1:
            values = list(values[0])

        i = 0

        while i < len(values):
            try:
                value = values[i]
                i += 1

                xpath = "".join(
                    [
                        '//*[@class="Question_type_scrambled-letters__unselected-box"]',
                        f'//button[@class="ScrambledLettersOption" and contains(text(), "{value.upper()}")]',
                    ]
                )

                locator = (By.XPATH, xpath)

                button = self.element.find_element(*locator)

                button.click()
            except NoSuchElementException as e:
                print(e)
                msg = "Invalid OpenAI completion answer, taking the 1st answer."
                self.logger.error(msg)

                # Try to find an letter in the unselected letters
                try:
                    xpath = '//*[@class="Question_type_scrambled-letters__unselected-box"]//button'
                    button = self.element.find_element(By.XPATH, xpath)
                    button.click()
                except NoSuchElementException:
                    self.logger.info(
                        "Did not found any more unselected letters, stopping to loop"
                    )
                    break

        submit_button = self.element.find_element(*SELECTORS["QUIZ"]["SUBMIT"])
        submit_button.click()

        correct_answer = self.get_correct_answer()

        if correct_answer:
            self.logger.info(f"Wrong answer, the correct answer is {correct_answer}.")
        else:
            self.logger.info("OpenAI returned a correct answer.")

        return correct_answer or values
