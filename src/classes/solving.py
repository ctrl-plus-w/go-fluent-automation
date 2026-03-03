"""Scraper handler section for the quiz tab"""

from selenium.common.exceptions import TimeoutException
from typing import TYPE_CHECKING

import sys
import chalk

from src.classes.questions.question import Question
from src.classes.activity import Activity
from src.classes.logger import Logger

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
        self.scraper.wait_for_element(
            locator, "Next button not found", timeout=10, to_be_clickable=True
        )
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
        """Handle a question."""
        locator = SELECTORS["QUIZ"]["QUESTION"]
        try:
            self.scraper.wait_for_element(
                locator, "Page didn't load. (didn't found the quiz question)"
            )
        except TimeoutException:
            # Dump quiz container HTML for debugging
            try:
                container = self.scraper.driver.find_element(*SELECTORS["QUIZ"]["CONTAINER"])
                html = container.get_attribute("outerHTML")
                with open("debug_quiz_html.txt", "w") as f:
                    f.write(html)
                self.logger.error(f"Quiz question not found. Dumped quiz HTML ({len(html)} chars) to debug_quiz_html.txt")
            except Exception as dump_err:
                self.logger.error(f"Quiz question not found and failed to dump HTML: {dump_err}")
            raise

        question_el = self.scraper.driver.find_element(*locator)
        question = Question.from_element(self.logger, question_el)

        if not question:
            classes = question_el.get_attribute("class")
            # Dump the full quiz container to understand the structure
            try:
                container = self.scraper.driver.find_element(*SELECTORS["QUIZ"]["CONTAINER"])
                html = container.get_attribute("outerHTML")
            except Exception:
                html = question_el.get_attribute("outerHTML")
            with open("debug_question_html.txt", "w") as f:
                f.write(html)
            self.logger.error(
                f"Did not find any question matching. Classes: '{classes}'. "
                f"Dumped quiz container HTML ({len(html)} chars) to debug_question_html.txt"
            )
            sys.exit()

        question_str = question.as_text()

        retrieved_question = self.activity.get_question(question_str)

        if retrieved_question:
            self.logger.info(
                chalk.bold(
                    chalk.blue(
                        "Found a retrieved question, using it and replacing the element."
                    )
                )
            )
            retrieved_question.element = question_el
            retrieved_question.first_use = False
            question = retrieved_question

        self.logger.info(
            chalk.bold(chalk.cyan(f"Loaded question with type '{question.type}'"))
        )

        answers = (
            ["SKIP"] if question.skip_completion else self.get_answer(question_str)
        )

        try:
            _value = answers[0]
        except (KeyError, IndexError):
            self.logger.debug(
                "Received an invalid value, resetting the answers variable."
            )
            answers = []

        question.correct_answer = question.answer(answers)

        if question.first_use:
            self.activity.questions.append(question)

    def retake_if_score_under(self, expected_score: int, max_retakes: int = 3):
        """Click the retake button if the score is under the expected score"""
        if not hasattr(self, '_retake_count'):
            self._retake_count = 0

        score = self.scraper.get_score()

        if score is not None and score < expected_score:
            self._retake_count += 1
            if self._retake_count > max_retakes:
                self.logger.info(
                    chalk.bold(chalk.yellow(
                        f"Reached max retakes ({max_retakes}). Accepting score of {score}%."
                    ))
                )
                return False
            self.logger.info(
                chalk.bold(chalk.yellow(
                    f"Retaking quiz (attempt {self._retake_count}/{max_retakes})."
                ))
            )
            self.scraper.retake()
            self.resolve_quiz()
            return True

        return False

    def resolve_quiz(self):
        """Answer to all the questions of the quiz"""
        self.logger.info("Resolving the quiz...")

        self.scraper.load_activity_page_and_tab(self.activity, "QUIZ_TAB")
        self.scraper.wait_for_element(
            SELECTORS["QUIZ"]["CONTAINER"], "Failed to load the quiz container."
        )

        # Click the "Démarrer" (Start) button if present
        try:
            self.scraper.wait_for_element(
                SELECTORS["QUIZ"]["START"],
                "No start button found",
                timeout=5,
                to_be_clickable=True,
            )
            start_button = self.scraper.driver.find_element(*SELECTORS["QUIZ"]["START"])
            start_button.click()
            self.logger.debug("Clicked the quiz start button.")
        except TimeoutException:
            self.logger.debug("No start button found, quiz may already be started.")

        has_all_cached_answers_been_used = bool(len(self.activity.questions)) and all(
            map(lambda q: q.cache_used or q.skip_completion, self.activity.questions)
        )
        self.logger.info(
            chalk.bold(
                chalk.blue(
                    f"Has all cached answers been used : {has_all_cached_answers_been_used}"
                )
            )
        )

        # In case something wrong happens and the cached answers are all used twice, we exit the resolving to avoid
        # infinite loops
        if has_all_cached_answers_been_used:
            msg = f"All questions have been used and it's trying to retake the quiz. Skipping. "
            self.logger.info(chalk.bold(chalk.yellow(msg)))
            return len(self.activity.questions)  # return the count of activities done

        while not self.scraper.is_finished():
            self.handle_question()
            self.set_next_question()

        score = self.scraper.get_score()

        msg = f"Finished the quiz with a score of {score}%."
        self.logger.info(chalk.bold(chalk.red(msg)))

        self.retake_if_score_under(100)
        return len(self.activity.questions)  # return the count of activities done
