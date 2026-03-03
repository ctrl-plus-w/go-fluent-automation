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


def generate_prompt(data: str, quiz_question: str):
    """Generate an OpenAPI completion prompt from the activity data and the quiz question"""
    return [
        {
            "role": "user",
            "content": "You are an polyglot language expert, you will receive some data about a question and you will have to responde to differents questions about these activities. Three types of questions will be prompted to you. You will need to ALWAYS responde as JSON an array of strings. And NEVER responde anything besides a JSON array of strings. The response MUST NOT be a JSON object. If multiple values are part of the response, they MUST be elements of the JSON array. If you need to complete a sentence, only return the missing part of the sentence that is marked as ____ but keep the result in a JSON array. Do NOT wrap the response in markdown code blocks.",
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


def get_answer(logger: Logger, data: str, quiz_question: str):
    """Get the OpenAI Completion answer from the activity data and the quiz question"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=generate_prompt(data, quiz_question),
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
        return get_answer(logger, data, quiz_question)
