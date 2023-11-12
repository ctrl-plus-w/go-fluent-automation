"""Dotenv module"""


class Dotenv:
    """Util class to handle .env files"""

    def __init__(self, path: str):
        self.path = path
        self.filecontent = None
        self.values = {}

        self.update_file()

    def update_values(self):
        """update the local values from the file content retrieve"""
        if self.filecontent is None:
            return

        self.values = {}

        for line in self.filecontent.split("\n"):
            line = line.split("#")[0]

            if line == "":
                continue

            key, value = line.split("=")
            self.values[key] = value.replace('"', "")

    def stringify_values(self):
        """Stringify the dictionnary as key value pairs with an equal separating the keys and the values"""
        pairs = []

        for key, value in self.values.items():
            pairs.append(f'{key}="{value}"')

        return "\n".join(pairs)

    def update_file(self):
        """Retrieve the file content (raw) and then update the values from that file content"""
        with open(self.path, encoding="utf-8") as f:
            self.filecontent = f.read()

        self.update_values()

    def push_values(self):
        """Push the local values to the dotenv file"""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(self.stringify_values())

    def get_key(self, key: str):
        """Retrieve a key from the dotenv file"""
        if not key in self.values:
            return None

        return self.values[key]

    def set_key(self, key: str, value: str):
        """Add or update a key from the dotenv file"""
        self.values[key] = value
        self.push_values()

    def remove_key(self, key: str):
        """Remove a key from the dotenv file"""
        del self.values[key]
        self.push_values()
