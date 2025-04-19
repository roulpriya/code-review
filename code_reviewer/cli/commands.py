#!/usr/bin/env python3

import logging
import os

from code_reviewer.reviewer import CodeReviewer

logger = logging.getLogger("code-reviewer")


def review_command() -> None:
    """Handle the 'review' command."""
    reviewer = CodeReviewer(
        project_path=os.getcwd(),
    )
    results = reviewer.review_project()
    reviewer.display_results(results)
