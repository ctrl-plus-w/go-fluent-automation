"""Scraper handler section for the quiz tab"""
from selenium.common.exceptions import TimeoutException
from logging import Logger
from typing import TYPE_CHECKING

import sys
import chalk

from src.classes.questions.question import Question
from src.classes.activity import Activity

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
            msg = f"Retrieving the cached response: '{question.correct_answer}'"
            self.logger.info(chalk.yellow(msg))
            question.cache_used = True
            return question.correct_answer

        self.logger.debug(f'Answering : "{chalk.bold(question_str.strip())}"')
        self.logger.info("Waiting for OpenAI's response.")
        answer = get_answer(self.logger, self.activity.data, question_str)
        self.logger.debug(f'OpenAI Completion responded with : "{chalk.bold(answer)}"')

        return answer

    def handle_question(self):
        """Handle a question. Lo"""
        locator = SELECTORS["QUIZ"]["QUESTION"]
        self.scraper.wait_for_element(locator, "Page didn't load. (didn't found the quiz question)")

        question_el = self.scraper.driver.find_element(*locator)
        question = Question.from_element(self.logger, question_el)

        question_str = question.as_text()

        retrieved_question = self.activity.get_question(question_str)

        if retrieved_question:
            self.logger.info(chalk.bold(chalk.blue("Found a retrieved question, using it and replacing the element.")))
            retrieved_question.element = question_el
            retrieved_question.first_use = False
            question = retrieved_question

        if not question:
            classes = question_el.get_attribute("class")
            self.logger.error(
                f"Did not found any question matching. Classes : '{classes}'"
            )
            sys.exit()

        self.logger.info(chalk.bold(chalk.cyan(f"Loaded question with type '{question.type}'")))

        answers = (["SKIP"] if question.skip_completion else self.get_answer(question_str))

        try:
            _value = answers[0]
        except KeyError:
            self.logger.debug(
                "Received an invalid value, resetting the answers variable."
            )
            answers = []

        question.correct_answer = question.answer(answers)

        if question.first_use:
            self.activity.questions.append(question)

    def retake_if_score_under(self, expected_score: int):
        """Click the retake button if the score is under the expected score"""
        score = self.scraper.get_score()

        if score is not None and score < expected_score:
            self.scraper.retake()
            self.resolve_quiz()
            return True

        return False

    def resolve_quiz(self):
        """Answer to all the questions of the quiz"""
        self.logger.info("Resolving the quiz...")

        self.scraper.load_activity_page_and_tab(self.activity, "QUIZ_TAB")
        self.scraper.wait_for_element(SELECTORS["QUIZ"]["CONTAINER"], "Failed to load the quiz container.")

        has_all_cached_answers_been_used = bool(len(self.activity.questions)) and all(
            map(lambda q: q.cache_used, self.activity.questions))
        self.logger.info(
            chalk.bold(chalk.blue(f"Has all cached answers been used : {has_all_cached_answers_been_used}")))
        print(list(map(lambda q: q.cache_used, self.activity.questions)))

        # In case something wrong happens and the cached answers are all used twice, we exit the resolving to avoid
        # infinite loops
        if has_all_cached_answers_been_used:
            msg = f"All questions have been used and it's trying to retake the quiz. Skipping. "
            self.logger.info(chalk.bold(chalk.yellow(msg)))
            return

        while not self.scraper.is_finished():
            self.handle_question()
            self.set_next_question()

        score = self.scraper.get_score()

        msg = f"Finished the quiz with a score of {score}%."
        self.logger.info(chalk.bold(chalk.red(msg)))

        self.retake_if_score_under(100)
