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
            "content": "You are an English expert, you will receive some data about an activity and you will have to responde to differents questions about these activities. Three types of questions will be prompted to you. You will need to ALWAYS responde as JSON arrays of strings. And NEVER responde anything besides JSON arrays of strings.",
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
        model="gpt-3.5-turbo-16k-0613", messages=generate_prompt(data, quiz_question)
    )

    content = response.choices[0].message.content
    print()

    return json.loads(content)
