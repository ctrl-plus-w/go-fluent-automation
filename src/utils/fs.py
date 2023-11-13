"""File systel utils module"""
import os


def create_directory(directory: str):
    """Create a directory if it doesn't exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
