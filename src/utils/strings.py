"""Strings utils module"""

from difflib import SequenceMatcher


def remove_quote(txt: str):
    """Remove all the quotes inside the string"""
    return txt.replace('"', "")


def escape(txt: str):
    """Escape a string"""
    return str(txt).translate(
        str.maketrans(
            {
                '"': "",
            }
        )
    )


def normalize(txt: str) -> str:
    """Normalize text for comparison: lowercase and collapse whitespace."""
    return " ".join(txt.strip().lower().split())


def fuzzy_match(value: str, option_text: str) -> bool:
    """Case-insensitive match with whitespace normalization and substring check."""
    v = normalize(value)
    o = normalize(option_text)
    return v == o or v in o or o in v


def best_match_index(value: str, options: list[str], threshold: float = 0.6):
    """Return the index of the best matching option using sequence matching.

    Returns None if no option exceeds the similarity threshold.
    """
    best_ratio = 0.0
    best_idx = None
    v = normalize(value)
    for i, opt in enumerate(options):
        ratio = SequenceMatcher(None, v, normalize(opt)).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_idx = i
    return best_idx if best_ratio > threshold else None
