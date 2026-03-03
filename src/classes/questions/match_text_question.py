"""Match text question module"""

from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.common.by import By

from src.classes.questions.question import Question

from src.constants.selectors import SELECTORS
from src.utils.strings import escape


class MatchTextQuestion(Question):
    """Match text question"""

    def as_text(self):
        # Extract word labels from span elements in the stem
        word_labels = []
        stem_text = ""
        try:
            stem = self.element.find_element(*SELECTORS["QUIZ"]["STEM"])
            stem_text = stem.text.strip()
            spans = stem.find_elements(By.CSS_SELECTOR, "span")
            word_labels = [s.text.strip() for s in spans if s.text.strip()]
        except NoSuchElementException:
            stem_text = self.element.text

        # Get definition choices from source container
        choices = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
        definitions = [c.text.strip() for c in choices if c.text.strip()]

        if not definitions:
            # Source container is empty (already answered / resumed quiz).
            # Fall back to full element text so the AI gets some context.
            self.question_str = stem_text or self.element.text
            return self.question_str

        # Format as a clear matching task so the AI returns definitions
        words_str = ", ".join(word_labels) if word_labels else "(see question)"
        defs_list = "\n".join([f"- {d}" for d in definitions])

        self.question_str = (
            f"Match each word with its correct definition. "
            f"Words in order: {words_str}\n"
            f"Available definitions:\n{defs_list}\n"
            f"Return ONLY the definitions (not the words) as a JSON array, "
            f"in the same order as the words above."
        )
        return self.question_str

    def get_correct_answer(self):
        """Get the correct answer from the explanation section"""
        try:
            items = self.element.find_elements(*SELECTORS["QUIZ"]["CORRECT_ANSWER_LIST"])
            if items:
                return [item.text.strip() for item in items if item.text.strip()]

            title = self.element.find_element(*SELECTORS["QUIZ"]["CORRECT_ANSWER_TITLE"])
            text = title.text.strip()
            if text:
                return text.split(", ")
            return None
        except NoSuchElementException:
            return None

    def get_random_option(self):
        """Get a random unselected option from the source container"""
        try:
            options = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
            return options[0] if options else None
        except NoSuchElementException:
            return None

    def can_answer(self):
        """Check if there are empty receiver slots"""
        receivers = self.element.find_elements(*SELECTORS["QUIZ"]["RECEIVER"])
        for receiver in receivers:
            if receiver.text.strip() == "":
                return True
        return False

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
        for value in values:
            try:
                self.logger.debug(f"Retrieving button with value: '{escape(value)}'")
                options = self.element.find_elements(*SELECTORS["QUIZ"]["SOURCE_OPTION"])
                clicked = False
                for option in options:
                    option_text = option.text.strip().lower()
                    value_text = value.strip().lower()
                    # Bidirectional substring match: handles both when
                    # AI returns full definitions or partial text
                    if value_text in option_text or option_text in value_text:
                        option.click()
                        clicked = True
                        break

                if not clicked:
                    self.logger.error(
                        "Invalid OpenAI completion answer, taking the 1st answer."
                    )
                    self.select_random_option()
            except (NoSuchElementException, InvalidSelectorException):
                self.logger.error(
                    "Invalid OpenAI completion answer, taking the 1st answer."
                )
                self.select_random_option()

        max_attempts = 50
        attempts = 0
        while self.can_answer() and attempts < max_attempts:
            if not self.get_random_option():
                self.logger.info("No source options left but receivers still empty.")
                break
            self.select_random_option()
            attempts += 1

        if attempts >= max_attempts:
            self.logger.info("Reached max attempts in match text cleanup loop.")

        return self.submit_and_check_correct_answer(values)
