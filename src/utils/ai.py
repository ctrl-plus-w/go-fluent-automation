"""Solver utils module"""

import json
import re

from openai import OpenAI, APITimeoutError

from src.classes.logger import Logger

from src.constants.credentials import OPENAI_API_KEY, OPENAI_ORGANIZATION

client = OpenAI(organization=OPENAI_ORGANIZATION, api_key=OPENAI_API_KEY)


def _strip_markdown_codeblock(text: str) -> str:
    """Strip markdown code block wrappers (```json ... ```) from OpenAI responses."""
    stripped = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    stripped = re.sub(r"\n?```\s*$", "", stripped)
    return stripped.strip()


QUESTION_TYPE_HINTS = {
    "Fill in gaps block question": (
        "This is a fill-in-the-blanks question where you select words from a list. "
        "Return the words in the order they fill the blanks. "
        "Each value MUST exactly match one of the listed options (case-sensitive)."
    ),
    "Fill in gaps text question": (
        "This is a fill-in-the-blanks question where you type the missing words. "
        "Return only the missing word(s), one per blank, in order."
    ),
    "Match text question": (
        "This is a matching question. Return ONLY the definitions/descriptions "
        "in the same order as the words listed. Each value MUST exactly match "
        "one of the available options."
    ),
    "Scrambled sentences question": (
        "This is a sentence completion or word-ordering question. "
        "If the available options are multi-word phrases, return the correct phrase(s) "
        "as COMPLETE strings (e.g. [\"Con vistas a\"]), do NOT split them into individual words. "
        "If the options are individual words, return them in the correct sentence order. "
        "Each value MUST exactly match one of the listed options."
    ),
    "Scrambled letters question": (
        "This is a letter-unscrambling question. Return the complete word as a single string."
    ),
    "Multiple choice text question": (
        "This is a multiple choice question. Return a single-element array "
        "with the text of the correct answer option."
    ),
    "Short answer text question": (
        "This is a free-text question. Return a single-element array with your answer."
    ),
}


def generate_prompt(data: str, quiz_question: str, question_type: str = ""):
    """Generate an OpenAPI completion prompt from the activity data and the quiz question"""
    base_instruction = (
        "You are a polyglot language expert. You will receive data about a language "
        "learning activity and must answer quiz questions about it. "
        "You MUST ALWAYS respond as a JSON array of strings. NEVER respond with "
        "anything besides a JSON array of strings. The response MUST NOT be a JSON object. "
        "If multiple values are part of the response, they MUST be elements of the JSON array. "
        "If you need to complete a sentence, only return the missing part of the sentence "
        "that is marked as ____ but keep the result in a JSON array. "
        "Do NOT wrap the response in markdown code blocks."
    )

    type_hint = QUESTION_TYPE_HINTS.get(question_type, "")
    if type_hint:
        base_instruction += f"\n\nQuestion type: {question_type}. {type_hint}"

    return [
        {
            "role": "user",
            "content": base_instruction,
        },
        {
            "role": "user",
            "content": f"The data is the following :\n{data}",
        },
        {
            "role": "user",
            "content": quiz_question,
        },
    ]


def get_answer(logger: Logger, data: str, quiz_question: str, question_type: str = ""):
    """Get the OpenAI Completion answer from the activity data and the quiz question"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=generate_prompt(data, quiz_question, question_type),
            timeout=10,
        )

        content = response.choices[0].message.content
        content = _strip_markdown_codeblock(content)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return [content]
    except APITimeoutError:
        logger.debug("OpenAI request timed out after 10 seconds, retrying the query.")
        return get_answer(logger, data, quiz_question, question_type)
