"""Credentials constants module"""
import os

from dotenv import load_dotenv


load_dotenv()

USERNAME = os.getenv("GOFLUENT_USERNAME")
PASSWORD = os.getenv("GOFLUENT_PASSWORD")

OPENAI_ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

assert USERNAME != "" and USERNAME is not None, "Missing GOFLUENT_USERNAME env variable"
assert PASSWORD != "" and PASSWORD is not None, "Missing GOFLUENT_PASSWORD env variable"

assert (
    OPENAI_API_KEY != "" and OPENAI_API_KEY is not None
), "Missing OPENAI_API_KEY env variable"
assert (
    OPENAI_ORGANIZATION != "" and OPENAI_ORGANIZATION is not None
), "Missing OPENAI_ORGANIZATION env variable"
