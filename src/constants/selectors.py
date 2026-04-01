"""Scraper selectors constants module"""
from selenium.webdriver.common.by import By

SELECTORS = {
    "LOGIN": {
        "SUBMIT_BUTTON": (
            By.CSS_SELECTOR,
            'button[type="submit"]',
        ),
        "DOMAIN": (
            By.ID,
            "outlined-size-normal",
        ),
    },
    "MICROSOFT": {
        "USERNAME_INPUT": (
            By.ID,
            'i0116',
        ),
        "PASSWORD_INPUT": (
            By.ID,
            "i0118",
        ),
        "SUBMIT_BUTTON": (
            By.ID,
            "idSIButton9",
        ),
        "STAY_SIGNED_IN": (
            By.XPATH,
            "//*[contains(text(), 'Stay signed in?')]",
        ),
        "FEEDBACK": (
            By.XPATH,
            "//*[contains(text(), 'Your account or password is incorrect.')]",
        ),
        "PICK_ACCOUNT_OTHER": (
            By.ID,
            "otherTile",
        )
    },
    "DASHBOARD": {
        "LOGO": (
            By.CSS_SELECTOR,
            ".header__logo",
        ),
        "MODAL_SKIP": (
            By.XPATH,
            '//span[contains(@class, "skipButton")]',
        ),
    },
    "PROFILE": {
        "LANGUAGE_ITEM": (
            By.XPATH,
            "//img[starts-with(@alt, 'flag')]/ancestor::div[contains(@class, 'profile-item_item')]",
        ),
        "LANGUAGE_VALUE": (
            By.CSS_SELECTOR,
            "div[class*='profile-item_content']",
        ),
        "LANGUAGE_FLAG": (
            By.CSS_SELECTOR,
            "img[alt^='flag']",
        ),
        "LANGUAGE_COMBOBOX": (
            By.CSS_SELECTOR,
            ".MuiAutocomplete-input",
        ),
        "LANGUAGE_OPEN_BUTTON": (
            By.CSS_SELECTOR,
            ".MuiAutocomplete-popupIndicator",
        ),
        "LANGUAGE_OPTION": (
            By.CSS_SELECTOR,
            "[role='option']",
        ),
    },
    "TRAINING": {
        "CONTAINER": (
            By.CSS_SELECTOR, ".training-page"
        ),
        "PAGINATION": (
            By.CSS_SELECTOR,
            ".pagination"
        ),
        "PAGINATION_ITEM": (
            By.CSS_SELECTOR,
            ".pagination-item"
        ),
        "BLOCK": (
            By.CSS_SELECTOR,
            '.training-card-block',
        ),
        "BLOCK_DATE": (
            By.CSS_SELECTOR,
            '.training-card-block__date',
        ),
        "BLOCK_CARD_BLOCK": (
            By.CSS_SELECTOR,
            '.training-card-block',
        ),
        "BLOCK_CARD": (
            By.CSS_SELECTOR,
            ".training-card",
        ),
        "BLOCK_CARD_LINK": (
            By.CSS_SELECTOR,
            '.training-card__link',
        ),
        "BLOCK_CARD_FLAG": (
            By.CSS_SELECTOR,
            "img[alt^='flag']",
        ),
    },
    "VOCABULARY": {
        "ACTIVITIES_CONTAINER": (
            By.XPATH,
            "/html/body/div/div[5]/main/div/div/div/div/div/div/div[1]/div/div/div[1]/div[3]/div/div/div/div[2]/div/div/div[1]",
        ),
        "ACTIVITIES_LIST": (
            By.CSS_SELECTOR,
            ".browse-all-activities__list",
        ),
    },
    "NAV": {
        "CONTAINER": (
            By.CSS_SELECTOR,
            ".tabs",
        ),
        "LEARNING_TAB": (
            By.CSS_SELECTOR,
            "#learn",
        ),
        "QUIZ_TAB": (
            By.CSS_SELECTOR,
            "#practice",
        ),
    },
    "ACTIVITY": {
        "TAB": (
            By.CSS_SELECTOR,
            ".HowtoNavigationSidebar__list > .HowtoNavigationSidebar__item",
        ),
        "HOWTO_NAVIGATION_SIDEBAR": (
            By.CSS_SELECTOR,
            ".HowtoNavigationSidebar",
        ),
        "SECTION": (
            By.CSS_SELECTOR,
            ".section",
        ),
    },
    "QUIZ": {
        "CONTAINER": (
            By.ID,
            "quiz",
        ),
        "START": (
            By.CSS_SELECTOR,
            "#quiz-button-start, #quiz-button-resume",
        ),
        "QUESTION": (
            By.CSS_SELECTOR,
            "[class*='quiz-common-question_container']",
        ),
        "SUBMIT": (
            By.ID,
            "quiz-button-submit",
        ),
        "NEXT": (
            By.ID,
            "quiz-button-next",
        ),
        "RETAKE": (
            By.XPATH,
            "//button[contains(@class, 'quiz-button_outlined')]",
        ),
        "VALUE": (
            By.CSS_SELECTOR,
            "[class*='quiz-score_score']",
        ),
        "END_PAGE": (
            By.CSS_SELECTOR,
            "[class*='quiz-end-page_container']",
        ),
        "SOURCE_CONTAINER": (
            By.ID,
            "source-container",
        ),
        "SOURCE_OPTION": (
            By.CSS_SELECTOR,
            "#source-container [role='button']",
        ),
        "RECEIVER": (
            By.CSS_SELECTOR,
            "[id^='receiver-']",
        ),
        "RADIO_OPTION": (
            By.CSS_SELECTOR,
            "label[role='radio']",
        ),
        "CORRECT_ANSWER_TITLE": (
            By.CSS_SELECTOR,
            "[class*='quiz-explanation_title']",
        ),
        "CORRECT_ANSWER_LIST": (
            By.CSS_SELECTOR,
            "li[class*='quiz-explanation_answer']",
        ),
        "INSTRUCTIONS": (
            By.CSS_SELECTOR,
            "[class*='quiz-common-question_instructions']",
        ),
        "STEM": (
            By.CSS_SELECTOR,
            "[class*='quiz-common-question_stem'],"
            " [class*='quiz-text-inputs_stem'],"
            " [class*='quiz-scrambled-letters_stem']",
        ),
    },
}
