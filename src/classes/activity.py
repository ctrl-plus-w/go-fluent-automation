"""Activity module"""


class Activity:
    """Activity class"""

    def __init__(self, url: str):
        self.url = url
        self.data = []
        self.questions = []

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
