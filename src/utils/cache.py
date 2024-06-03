import os

from typing import List

FILENAME = "cache.txt"


def get_cached_urls():
    cached_urls = set()

    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            cached_urls.update(f.read().strip().split("\n"))

    return cached_urls


def add_to_cache(urls: List[str]):
    cached_urls = get_cached_urls()

    cached_urls.update(urls)
    with open(FILENAME, "w+") as f:
        f.write("\n".join(cached_urls))


def is_in_cache(url: str):
    if not os.path.exists(FILENAME):
        return False

    return url in get_cached_urls()


def clear_cache():
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
