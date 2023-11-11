"""Strings utils module"""


def remove_quote(txt: str):
    """Remove all the quotes inside the string"""
    return txt.replace('"', "")
