"""Solver utils module"""
import json

from openai import OpenAI

from src.constants.credentials import OPENAI_API_KEY, OPENAI_ORGANIZATION

client = OpenAI(organization=OPENAI_ORGANIZATION, api_key=OPENAI_API_KEY)


def generate_prompt(data: str, quiz_question: str):
    """Generate an OpenAPI completion prompt from the activity data and the quiz question"""
    return [
        {
            "role": "user",
            "content": "You are an English expert, you will receive some data about an activity and you will have to responde to differents questions about these activities. Three types of questions will be prompted to you. You will need to ALWAYS responde as JSON an array of strings. And NEVER responde anything besides a JSON array of strings. The response MUST NOT be a JSON object. If multiple values are part of the response, they MUST be elements of the JSON array. If you need to complete a sentence, only return the missing part of the sentence that is marked as ____ but keep the result in a JSON array.",
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


def get_answer(data: str, quiz_question: str):
    """Get the OpenAI Completion answer from the activity data and the quiz question"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=generate_prompt(data, quiz_question),
        timeout=8,
    )

    print(response.choices)
    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return [content]


# def get_timed_answer(data: str, quiz_question: str, max_timeout: int):
