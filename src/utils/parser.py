"""Parse module"""

from typing import Dict
from bs4 import BeautifulSoup

from src.utils.lists import _f, _m


def get_section_type(soup: BeautifulSoup) -> str:
    """Get the section type from the HTML"""
    section = soup.select_one(".section")

    section_classes = section.get("class")

    if "section_titleSlide_yes" in section_classes:
        return "TITLE"

    if "section_summarySlide_yes" in section_classes:
        return "SUMMARY"

    vocab_cols_images_sets_len = len(soup.select(".SetsAudsImgsSlide__set"))
    vocab_rows_images_sets_len = len(soup.select(".MimgSetAudSlide__set"))
    vocab_rows_sets_len = len(soup.select(".SetsAudsSlide__set"))

    # Make sure that only one of the three choices is positive
    # and that at least one of the choices is positive
    sets = [vocab_cols_images_sets_len, vocab_rows_images_sets_len, vocab_rows_sets_len]

    assert (
        len(_f(lambda s: s > 0, sets)) == 1 or len(_f(lambda s: s != 0, sets)) == 1
    ), "Cannot determine the type of the section."

    if vocab_cols_images_sets_len > 0:
        return "VOCABULARY_COLS_IMAGES"

    if vocab_rows_images_sets_len:
        return "VOCABULARY_ROWS_IMAGES"

    if vocab_rows_sets_len:
        return "VOCABULARY_ROWS"


def handle_title_section(soup: BeautifulSoup) -> Dict[str, str]:
    """Get the data from a title section"""
    title = soup.select_one("h3.TitleSlide__title").text.strip()
    desc = soup.select_one("p.TitleSlide__objective").text.strip()

    return {"title": title, "description": desc}


def handle_summary_section(soup: BeautifulSoup) -> Dict[str, str]:
    """Get the data from a summary section"""
    section_main = soup.select_one(".section__main")
    return {"data": section_main.text.strip()}


def handle_vocab(soup: BeautifulSoup, set_classname: str) -> Dict[str, str]:
    """Handle a vocabulary section"""
    sets = soup.select(set_classname)

    defs = []
    data = []

    for s in sets:
        key_phrases = s.findChildren("span", {"class": "key-phrase"}, recursive=True)
        audio_buttons = s.findChildren("div", {"class": "AudioButton"}, recursive=True)

        if len(key_phrases) > 0 and len(audio_buttons) > 0:
            key_phrase_el = key_phrases[0]
            key_phrase = key_phrase_el.text
            key_phrase_el.decompose()

            defs.append({"key": key_phrase.strip(), "value": s.text.strip()})
        else:
            data.append(s.text.strip())

    title = soup.select_one("h3.section-header")

    return {"definitions": defs, "data": data, "title": title.text.strip()}


def handle_vocab_cols_images(soup: BeautifulSoup) -> Dict[str, str]:
    """Get the data from a vocabulary as columns with images section"""
    return handle_vocab(soup, ".SetsAudsImgsSlide__set")


def handle_vocab_rows_images(soup: BeautifulSoup) -> Dict[str, str]:
    """Get the data from a vocabulary as rows with images section"""
    return handle_vocab(soup, ".MimgSetAudSlide__set")


def handle_vocab_rows(soup: BeautifulSoup) -> Dict[str, str]:
    """Get the data from a vocabulary (or raw text) as rows (without images) section"""
    return handle_vocab(soup, ".SetsAudsSlide__set")


def get_data_from_section(section_html: str) -> Dict:
    """Get the data from the section HTML"""
    soup = BeautifulSoup(section_html, features="html.parser")

    section_type = get_section_type(soup)

    funcs = {
        "TITLE": handle_title_section,
        "SUMMARY": handle_summary_section,
        "VOCABULARY_COLS_IMAGES": handle_vocab_cols_images,
        "VOCABULARY_ROWS_IMAGES": handle_vocab_rows_images,
        "VOCABULARY_ROWS": handle_vocab_rows,
    }

    return {"type": section_type, **funcs[section_type](soup)}


def get_match_text_question_as_text(question_html: str):
    """Get the match type question as text"""
    soup = BeautifulSoup(question_html, features="html.parser")

    answers = []

    for answer in soup.select(".Question__options > button"):
        answers.append(answer.text)
        answer.decompose()

    for answer_input in soup.select(".Stem__answer"):
        new_tag = soup.new_tag("p")
        new_tag.string = "____\n"

        answer_input.replace_with(new_tag)

    answers_as_txt = "\n".join(_m(lambda t: f"- {t}", answers))

    return soup.text.strip() + "\n" + answers_as_txt


def get_green_text_correct_answer(question_html: str):
    """Get the match text question correct answers as a list
    (returns None if there's no correct answer div)"""
    soup = BeautifulSoup(question_html, features="html.parser")

    green_text = soup.find("p", {"style": "color: green;"}, recursive=True)

    if not green_text:
        return None

    content = green_text.select_one("div")

    return content.text


def get_match_text_question_correct_answers(question_html: str):
    """Get the match text question correct answers as a list
    (returns None if there's no correct answer div)"""

    content = get_green_text_correct_answer(question_html)

    if not content:
        return None

    return content.split(", ")


def get_fill_gaps_text_question_text_as_text(question_html: str):
    """Get the match type question as text"""
    soup = BeautifulSoup(question_html, features="html.parser")

    for answer_input in soup.select("input.Stem__answer_non-arabic"):
        new_tag = soup.new_tag("p")
        new_tag.string = "____"

        answer_input.replace_with(new_tag)

    return soup.text.strip()


def get_fill_gaps_block_question_as_text(question_html: str):
    """Get the match type question blocks output as text"""
    soup = BeautifulSoup(question_html, features="html.parser")

    answers = []

    for answer in soup.select(".Question__fill-button"):
        answers.append(answer.text)
        answer.decompose()

    for answer_input in soup.select(".Stem__answer"):
        new_tag = soup.new_tag("p")
        new_tag.string = "____"

        answer_input.replace_with(new_tag)

    answers_as_txt = "\n".join(_m(lambda t: f"- {t}", answers))

    return soup.text.strip() + "\n" + answers_as_txt
