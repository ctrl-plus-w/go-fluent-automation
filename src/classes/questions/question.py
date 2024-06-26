"""Activity quiz questions modules"""
from logging import Logger

import chalk

from selenium.webdriver.remote.webelement import WebElement

from src.utils.lists import _m

from src.constants.selectors import SELECTORS


class Question:
    """Activity quiz question interface"""

    def __init__(self, logger: Logger, q_type: str, element: WebElement):
        self.logger = logger
        self.type = q_type
        self.element = element
        self.question_str = ""
        self.correct_answer = None
        self.skip_completion = False
        self.cache_used = False
        self.first_use = True

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
            self.logger.info(chalk.green(f"Correct answer. Caching : '{values}'"))

        return correct_answer or values

    @staticmethod
    def from_element(logger: Logger, element: WebElement):
        """Get the appropriate Question sub-class for the element"""

        from src.classes.questions.scrambled_sentences_question import (
            ScrambledSentencesQuestion,
        )
        from src.classes.questions.multi_choice_image_question import (
            MultiChoiceImageQuestion,
        )
        from src.classes.questions.scrambled_letters_question import (
            ScrambledLettersQuestion,
        )
        from src.classes.questions.multi_choice_text_question import (
            MultiChoiceTextQuestion,
        )
        from src.classes.questions.fill_gaps_block_question import FillGapsBlockQuestion
        from src.classes.questions.fill_gaps_text_question import FillGapsTextQuestion
        from src.classes.questions.match_text_question import MatchTextQuestion
        from src.classes.questions.short_text_question import ShortTextQuestion

        curr_classes = element.get_attribute("class").split(" ")

        def has_all_classes(classes: list[str]):
            """Check if the element has all the classes passed"""
            return all(_m(lambda c: c in curr_classes, classes))

        otp_block = "Question_output_text-blocks"
        otp_text = "Question_output_text"
        otp_img = "Question_output_picture"
        otp_text_mult = "Question_output_text-multiple"

        if (
                has_all_classes(["Question_type_multiple-choice", otp_text])
                or has_all_classes(["Question_type_multiple-choice", otp_text_mult])
                or has_all_classes(["Question_type_true-or-false", otp_text])
        ):
            m = otp_text_mult in curr_classes
            return MultiChoiceTextQuestion(logger, "Multiple choice text question", element, m)

        if has_all_classes(["Question_type_scrambled-letters", otp_text]):
            return ScrambledLettersQuestion(logger, "Scrambled letters question", element)

        if has_all_classes(["Question_type_scrambled-sentence", otp_block]):
            return ScrambledSentencesQuestion(logger, "Scrambled sentences question", element)

        if has_all_classes(["Question_type_match-text", otp_block]):
            return MatchTextQuestion(logger, "Match text block question", element)

        if has_all_classes(["Question_type_fill-in-the-gaps", otp_text]):
            return FillGapsTextQuestion(logger, "Fill in gaps text question", element)

        if has_all_classes(["Question_type_fill-in-the-gaps", otp_block]):
            return FillGapsBlockQuestion(logger, "Fill in gaps block question", element)

        if has_all_classes(["Question_type_short-answer", otp_text]):
            return ShortTextQuestion(logger, "Short answer text question", element)

        if has_all_classes(["Question_type_multiple-choice", otp_img]):
            return MultiChoiceImageQuestion(logger, "Multiple choice image question", element)

        return None
