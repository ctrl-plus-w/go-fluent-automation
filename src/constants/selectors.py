"""Scraper selectors constants module"""
from selenium.webdriver.common.by import By

SELECTORS = {
    "LOGIN": {
        "USERNAME_INPUT": (
            By.XPATH,
            "/html/body/div/main/div[2]/div/div/div/div/div/div/div/div[1]/form/div/input[1]",
        ),
        "PASSWORD_INPUT": (
            By.XPATH,
            "/html/body/div/main/div[2]/div/div/div/div/div/div/div/div[1]/form/div/input[2]",
        ),
        "SUBMIT_BUTTON": (
            By.XPATH,
            "/html/body/div/main/div[2]/div/div/div/div/div/div/div/div[1]/form/div/button",
        ),
    },
    "DASHBOARD": {
        "LOGO": (
            By.XPATH,
            "/html/body/div/div[5]/nav[1]/div/div[1]/div[1]",
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
    },
}
