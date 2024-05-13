"""Activity module"""
from datetime import datetime
from typing import Optional

from src.classes.questions.question import Question


class Activity:
    """Activity class"""

    def __init__(self, url: str, date: Optional[datetime] = None):
        self.url = url
        self.date = date
        self.data = []
        self.questions: list[Question] = []
        self.valid = None

    def get_question(self, question_str: str):
        """Get the question by its question as string"""
        for question in self.questions:
            if question.question_str == question_str:
                return question

        return None

    def as_markdown(self):
        """Return the activity data as markdown"""
        lines = []

        for data in self.data:
            if data["type"] == "TITLE":
                lines.append(f"# {data['title']}")
                lines.append(f"{data['description']}  ")

            if data["type"].startswith("VOCABULARY"):
                lines.append("")
                lines.append(f"## {data['title']}")

                for definition in data["definitions"]:
                    lines.append(f"- {definition['key']} : {definition['value']}  ")

                for line in data["data"]:
                    lines.append(f"{line}  ")

            if data["type"] == "SUMMARY":
                lines.append("")
                lines.append("## Summary")
                lines.append(f"{data['data']} . ")

        return "\n".join(lines)
