"""Scraper handler section for the quiz tab"""
from logging import Logger
from typing import TYPE_CHECKING

import sys
import time
import chalk


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

    def set_next_question(self):
        """Set the next question"""
        locator = SELECTORS["QUIZ"]["NEXT"]
        button = self.scraper.driver.find_element(*locator)
        button.click()

    def get_answer(self, question_str: str):
        """Get the cached answer or the OpenAI Completion answer"""
        question = self.activity.get_question(question_str)

        if question and question.correct_answer:
            self.logger.info(
                chalk.yellow(
                    f"Retrieving the cached response: '{question.correct_answer}'"
                )
            )
            return question.correct_answer

        self.logger.info(f'Answering : "{chalk.bold(question_str.strip())}"')
        self.logger.info("Waiting for OpenAI's response.")
        answer = get_answer(self.activity.data, question_str)

        return answer

    def handle_question(self):
        """Handle a question."""
        locator = SELECTORS["QUIZ"]["QUESTION"]
        self.scraper.wait_for_element(locator, "Page didn't load.")

        question_el = self.scraper.driver.find_element(*locator)
        question = Question.from_element(self.logger, question_el)

        if not question:
            classes = question_el.get_attribute("class")
            self.logger.info(
                f"Did not found any question matching. Classes : '{classes}'"
            )
            sys.exit()

        question_str = question.as_text()

        answers = self.get_answer(question_str)

        question.correct_answer = question.answer(answers)
        self.activity.questions.append(question)

    def retake_if_score_under(self, expected_score: int):
        """Click the ratake button if the score is under the expected score"""
        score = self.scraper.get_score()

        if not score is None and score < expected_score:
            self.scraper.retake()
            self.resolve_quiz()
            return True

        return False

    def resolve_quiz(self):
        """Answer to all the questions of the quiz"""
        self.logger.info("Resolving the quiz...")

        self.scraper.load_activity_page_and_tab(self.activity, "QUIZ_TAB")

        if self.retake_if_score_under(100):
            return

        while not self.scraper.is_finished():
            self.handle_question()
            time.sleep(2)
            self.set_next_question()

        score = self.scraper.get_score()

        self.logger.info(
            chalk.bold(chalk.red(f"Finished the quiz with a score of {score}%."))
        )

        self.retake_if_score_under(100)
