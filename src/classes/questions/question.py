"""Activity quiz questions modules"""

from logging import Logger

import chalk
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

    # Feedback headings that indicate correct/wrong status — never the answer itself.
    # Only exact matches (after normalization) are filtered. Phrases like
    # "La bonne réponse est -" are NOT filtered because they indicate a wrong
    # answer where the correction list should be found.
    _FEEDBACK_EXACT = {
        "bonne réponse", "mauvaise réponse", "good answer", "wrong answer",
        "correct", "incorrect", "correct answer", "bien", "mal",
        "les bonnes réponses sont", "la bonne réponse est",
    }

    def _is_feedback_text(self, text: str) -> bool:
        """Check if text is a feedback heading rather than an actual answer."""
        normalized = text.strip().lower().rstrip("!.- ")
        return normalized in self._FEEDBACK_EXACT

    def get_correct_answer(self):
        """Return the value of the correct answer from the explanation section.

        Searches within the question element first, then falls back to the
        document root (driver) in case the explanation renders outside the
        question container.

        Only returns values from the answer list items (ul li). The title
        element contains feedback text ("Bonne réponse !") and is only used
        as a fallback when it clearly contains an actual answer.
        """
        # Search within the question element, then from the document root
        for context in [self.element, self.element.parent]:
            try:
                items = context.find_elements(
                    *SELECTORS["QUIZ"]["CORRECT_ANSWER_LIST"]
                )
                if items:
                    result = [item.text.strip() for item in items if item.text.strip()]
                    if result:
                        return result

                # The title element usually contains feedback text like
                # "Bonne réponse !" — only use it if it looks like an actual answer.
                title = context.find_element(
                    *SELECTORS["QUIZ"]["CORRECT_ANSWER_TITLE"]
                )
                text = title.text.strip()
                if text and not self._is_feedback_text(text):
                    return [text]
            except NoSuchElementException:
                continue

        self.logger.debug("get_correct_answer returned None (answer may be correct).")

        return None

    def as_text(self):
        """Return the question as text"""
        return self.element.text

    def answer(self, _value: str):
        """Answer the value and return the correct answer"""
        return []

    def submit_and_check_correct_answer(self, values: list[str]):
        """Submit the question and check if the returned response is correct"""
        try:
            submit_button = self.element.find_element(*SELECTORS["QUIZ"]["SUBMIT"])
        except NoSuchElementException:
            # Submit button is outside the question container in the new layout.
            # Use the WebDriver (element.parent) to search from the document root.
            try:
                submit_button = self.element.parent.find_element(
                    *SELECTORS["QUIZ"]["SUBMIT"]
                )
            except NoSuchElementException:
                self.logger.error(
                    "Submit button not found (may be hidden/disabled). "
                    "Returning values as-is."
                )
                return values

        submit_button.click()

        # Wait for the post-submit state (explanation + next button) to render
        driver = self.element.parent
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(SELECTORS["QUIZ"]["NEXT"])
            )
        except TimeoutException:
            self.logger.debug("Post-submit wait for Next button timed out.")

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
        """Get the appropriate Question sub-class for the element.

        Detects question type from DOM structure rather than CSS classes,
        since the new quiz uses CSS modules with hashed class names.
        """

        from src.classes.questions.fill_gaps_block_question import FillGapsBlockQuestion
        from src.classes.questions.fill_gaps_text_question import FillGapsTextQuestion
        from src.classes.questions.match_text_question import MatchTextQuestion
        from src.classes.questions.multi_choice_image_question import (
            MultiChoiceImageQuestion,
        )
        from src.classes.questions.multi_choice_text_question import (
            MultiChoiceTextQuestion,
        )
        from src.classes.questions.scrambled_letters_question import (
            ScrambledLettersQuestion,
        )
        from src.classes.questions.scrambled_sentences_question import (
            ScrambledSentencesQuestion,
        )
        from src.classes.questions.short_text_question import ShortTextQuestion

        def has(css):
            return len(element.find_elements(By.CSS_SELECTOR, css)) > 0

        # Multiple choice: has radio button options
        if has("label[role='radio']"):
            if has("label[role='radio'] img"):
                return MultiChoiceImageQuestion(
                    logger, "Multiple choice image question", element
                )
            return MultiChoiceTextQuestion(
                logger, "Multiple choice text question", element
            )

        # Short answer: has a textarea for free text input
        if has("textarea"):
            return ShortTextQuestion(logger, "Short answer text question", element)

        # Fill gaps text: has text input fields for typing answers
        if has("input[type='text']"):
            return FillGapsTextQuestion(logger, "Fill in gaps text question", element)

        # Drag-and-drop types: use source container with clickable chips
        if has("#source-container"):
            source_options = element.find_elements(
                By.CSS_SELECTOR, "#source-container [role='button']"
            )

            # Single-character chips → scrambled letters
            if source_options and all(len(o.text.strip()) <= 1 for o in source_options):
                return ScrambledLettersQuestion(
                    logger, "Scrambled letters question", element
                )

            # Check for receiver drop targets
            receivers = element.find_elements(By.CSS_SELECTOR, "[id^='receiver-']")

            if receivers:
                # Multiple receivers → match text (each receiver pairs with a word)
                # or fill gaps block (receivers as blanks in a sentence).
                # GoFluent uses quiz-scrambled-letters_stem for both match and
                # scrambled types, so check receiver count instead of stem class.
                if len(receivers) > 1:
                    # Check if receivers are inline within a stem sentence
                    # (fill gaps block) vs paired with word labels (match text).
                    # Look for stems in both quiz-common-question and
                    # quiz-scrambled-letters modules.
                    stem_els = element.find_elements(
                        By.CSS_SELECTOR,
                        "[class*='quiz-common-question_stem'],"
                        " [class*='quiz-scrambled-letters_stem']",
                    )
                    if stem_els:
                        stem = stem_els[0]
                        # Count non-receiver text children (word labels).
                        # Match text has labels like <span><p>Word</p></span>
                        # adjacent to each receiver.
                        text_labels = stem.find_elements(By.CSS_SELECTOR, "span")
                        if text_labels:
                            return MatchTextQuestion(
                                logger, "Match text question", element
                            )
                        # No text labels → fill gaps block
                        return FillGapsBlockQuestion(
                            logger, "Fill in gaps block question", element
                        )
                    # Fallback: multiple receivers → match text
                    return MatchTextQuestion(logger, "Match text question", element)

                # Single receiver → scrambled sentences
                return ScrambledSentencesQuestion(
                    logger, "Scrambled sentences question", element
                )

            # Source container without receivers → scrambled sentences
            return ScrambledSentencesQuestion(
                logger, "Scrambled sentences question", element
            )

        return None
