#!/usr/bin/env python3

import logging

logger = logging.getLogger("code-reviewer")

def read_file_content(file_path: str) -> str:
    """Read the content of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The file content as a string
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # Try with another encoding if utf-8 fails
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            return ""
    except Exception as e:
        logger.warning(f"Error reading file {file_path}: {e}")
        return ""
