"""Scrambled sentences block output question module"""

from selenium.common.exceptions import NoSuchElementException

from src.classes.questions.question import Question
from src.constants.selectors import SELECTORS
from src.utils.strings import escape


class ScrambledSentencesQuestion(Question):
    """Scrambled sentences block output question"""

    def as_text(self):
        # Get the stem/instructions text
        stem_text = ""
        try:
            stem = self.element.find_element(*SELECTORS["QUIZ"]["STEM"])
            stem_text = stem.text.strip()
        except NoSuchElementException:
            stem_text = self.element.text

        # Get available word choices from source container, sorted so that
        # reshuffled versions of the same question produce the same key.
        choices = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
        sorted_choices = sorted([c.text.strip() for c in choices])
        choices_text = "\n".join([f"- {c}" for c in sorted_choices])

        self.question_str = f"{stem_text}\n{choices_text}"
        return self.question_str

    def get_correct_answer(self):
        try:
            items = self.element.find_elements(
                *SELECTORS["QUIZ"]["CORRECT_ANSWER_LIST"]
            )
            if items:
                return [item.text.strip() for item in items if item.text.strip()]

            title = self.element.find_element(
                *SELECTORS["QUIZ"]["CORRECT_ANSWER_TITLE"]
            )
            text = title.text.strip()
            if text:
                return [text]
            return None
        except NoSuchElementException:
            return None

    def can_answer(self):
        """Check if there are empty receiver slots or remaining source options"""
        receivers = self.element.find_elements(*SELECTORS["QUIZ"]["RECEIVER"])
        for receiver in receivers:
            if receiver.text.strip() == "":
                return True
        # Single-receiver layouts: receiver has text but may still need more chips
        options = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
        return len(options) > 0

    def get_random_option(self):
        """Get a random unselected option from the source container"""
        try:
            options = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
            return options[0] if options else None
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
            self.logger.debug("Did not find any random options.")

    def answer(self, values: list[str]):
        initial_options = self.element.find_elements(
            *SELECTORS["QUIZ"]["SOURCE_OPTION"]
        )
        if not initial_options:
            self.logger.info(
                "No source options available (question may already be answered). "
                "Submitting as-is."
            )
            return self.submit_and_check_correct_answer(values)

        initial_source_count = len(initial_options)

        for value in values:
            try:
                self.logger.debug(f"Retrieving button with value: '{escape(value)}'")
                options = self.element.find_elements(
                    *SELECTORS["QUIZ"]["SOURCE_OPTION"]
                )
                clicked = False
                for option in options:
                    if value.strip().lower() in option.text.strip().lower():
                        option.click()
                        clicked = True
                        break

                if not clicked:
                    # Value may be the full sentence (from cached correct answer).
                    # Find all source options that appear as substrings and click
                    # them in sentence order.
                    matches = []
                    for opt in self.element.find_elements(
                        *SELECTORS["QUIZ"]["SOURCE_OPTION"]
                    ):
                        opt_text = opt.text.strip().lower()
                        pos = value.strip().lower().find(opt_text)
                        if pos >= 0:
                            matches.append((pos, opt))
                    if matches:
                        matches.sort(key=lambda x: x[0])
                        for _, opt in matches:
                            opt.click()
                        clicked = True

                if not clicked:
                    self.logger.error(
                        "Invalid OpenAI completion answer, taking the 1st answer."
                    )
                    self.select_random_option()
            except NoSuchElementException:
                self.logger.error(
                    "Invalid OpenAI completion answer, taking the 1st answer."
                )
                self.select_random_option()

        # Only fill remaining slots for "rearrange all" questions where
        # the AI intended to place every chip.  For "choose one" questions
        # (fewer AI values than source options), remaining chips are
        # distractors and must NOT be clicked.
        if len(values) >= initial_source_count:
            max_attempts = 50
            attempts = 0
            while self.can_answer() and attempts < max_attempts:
                if not self.get_random_option():
                    self.logger.info(
                        "No source options left but receivers still empty."
                    )
                    break
                self.select_random_option()
                attempts += 1

        return self.submit_and_check_correct_answer(values)
