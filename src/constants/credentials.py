"""Credentials constants module"""
import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

assert (
        OPENAI_API_KEY != "" and OPENAI_API_KEY is not None
), "Missing OPENAI_API_KEY env variable"
assert (
        OPENAI_ORGANIZATION != "" and OPENAI_ORGANIZATION is not None
), "Missing OPENAI_ORGANIZATION env variable"
