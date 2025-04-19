#!/usr/bin/env python3

import logging

from code_reviewer.cli.commands import review_command

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("code-reviewer")


def main() -> None:
    review_command()
