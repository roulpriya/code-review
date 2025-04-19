import logging
import os

logger = logging.getLogger("code-reviewer")

def tree(path):
    """List all files in a directory and its subdirectories.

    Args:
        path (str): The directory to list files from.

    Returns:
        list: A list of file paths.
    """
    file_paths = []

    for root, _, files in os.walk(path, topdown=True):
        for file in files:
            file_paths.append(os.path.join(root, file))

    return file_paths

def read_file_content(file_path: str) -> str:
    """Read the content of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return str(e)
