"""Scraper selectors constants module"""
from selenium.webdriver.common.by import By

SELECTORS = {
    "LOGIN": {
        "SUBMIT_BUTTON": (
            By.XPATH,
            '/html/body/div/div/div/div/div[2]/form/div/div[2]/button',
        ),
        "DOMAIN": (
            By.ID,
            "outlined-size-normal",
        ),
    },
    "MICROSOFT" : {
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
        "STAY_SIGNED_IN" : (
            By.XPATH,
            "//*[contains(text(), 'Stay signed in?')]",
        ),
        "FEEDBACK": (
            By.XPATH,
            "//*[contains(text(), 'Your account or password is incorrect.')]",
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
        )
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
            By.CSS_SELECTOR,
            ".QuizContainer"
        ),
        "QUESTION": (
            By.CSS_SELECTOR,
            ".Question",
        ),
        "ANSWER": (
            By.CSS_SELECTOR,
            ".Question__option",
        ),
        "CORRECT_ANSWER": (
            By.XPATH,
            "//p[contains(@style, 'color: green;')]",
        ),
        "SUBMIT": (
            By.CSS_SELECTOR,
            ".Question__submit",
        ),
        "NEXT": (
            By.CSS_SELECTOR,
            ".Question__next",
        ),
        "RETAKE": (
            By.CSS_SELECTOR,
            ".QuizResults__retake",
        ),
        "VALUE": (
            By.CSS_SELECTOR,
            ".QuizResults__value",
        ),
    },
}
