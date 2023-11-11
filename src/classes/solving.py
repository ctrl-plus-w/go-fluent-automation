"""Scraper handler section for the quiz tab"""
from logging import Logger
from typing import TYPE_CHECKING

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


from src.classes.activity import Activity
from src.classes.question import Question

from src.utils.ai import get_answer

from src.constants.selectors import SELECTORS

if TYPE_CHECKING:
    from src.classes.scraper import Scraper


class ActivitySolving:
    """Scraper handler section for the quiz tab"""

    def __init__(self, logger: Logger, scraper: "Scraper", activity: Activity):
        self.scraper = scraper
        self.logger = logger
        self.activity = activity

    def get_correct_answer(self):
        """Get the correct answer (text in green) of the quiz question"""
        try:
            locator = SELECTORS["QUIZ"]["CORRECT_ANSWER"]
            correct_answer = self.scraper.driver.find_element(*locator)

            to_delete = correct_answer.find_element(By.CLASS_NAME, "language_fr")
            to_delete.decompose()

            return correct_answer.get_attribute("innerText")

        except NoSuchElementException:
            self.logger.info(
                "Did not found any answer correcting. That might be because the answer was correct."
            )
            return None

    def handle_question(self):
        """Handle a question."""
        locator = SELECTORS["QUIZ"]["QUESTION"]
        self.scraper.wait_for_element(locator, "Page didn't load.")

        question_el = self.scraper.driver.find_element(*locator)
        question = Question.from_element(self.logger, question_el)

        if not question:
            # TODO : Handle if no question / put a random value.
            return

        question_str = question.as_text()

        self.logger.info(f'Answering : "{question_str.strip()}"')

        self.logger.info("Waiting for OpenAI's response.")
        answers = get_answer(self.activity.data, question_str)
        self.logger.info(f"OpenAI Answer is : {answers}")

        question.correct_answer = question.answer(answers)
        self.activity.questions.append(question)

    def resolve_quiz(self):
        """Answer to all the questions of the quiz"""
        self.logger.info("Resolving the quiz...")

        self.scraper.load_activity_page_and_tab(self.activity, "QUIZ_TAB")

        # TODO : Loop while there are remaining questions
        self.handle_question()
