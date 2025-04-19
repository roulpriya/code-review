#!/usr/bin/env python3

import json
from typing import Dict, Any


def colorize(text: str, color_code: str) -> str:
    """Add ANSI color codes to text."""
    return f"{color_code}{text}\033[0m"


# ANSI color codes
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"


def format_review_output(review_data: Dict[str, Any]) -> str:
    """Convert JSON review data into colorful markdown output."""
    
    # Handle empty review or error cases
    if not review_data or not isinstance(review_data, dict):
        return colorize("No valid review data to display", RED)
    
    # Extract data
    issues = review_data.get("issues", [])
    summary = review_data.get("summary", "No summary provided")
    file_name = review_data.get("file", "Unknown file")
    
    # Build the output
    output = []
    
    # Header
    output.append(colorize(f"# Code Review: {file_name}", BOLD + BLUE))
    output.append("")
    
    # Summary
    output.append(colorize("## Summary", BOLD + CYAN))
    output.append(colorize(summary, CYAN))
    output.append("")
    
    # Issues
    if not issues:
        output.append(colorize("No issues found.", GREEN))
    else:
        output.append(colorize(f"## Issues ({len(issues)})", BOLD + YELLOW))
        
        # Group issues by severity
        severity_groups = {"high": [], "medium": [], "low": []}
        for issue in issues:
            severity = issue.get("severity", "low").lower()
            severity_groups.get(severity, []).append(issue)
        
        # Display issues by severity
        for severity, severity_issues in [
            ("high", severity_groups["high"]), 
            ("medium", severity_groups["medium"]), 
            ("low", severity_groups["low"])
        ]:
            if not severity_issues:
                continue
                
            color = RED if severity == "high" else YELLOW if severity == "medium" else CYAN
            
            output.append(colorize(f"### {severity.upper()} Severity Issues ({len(severity_issues)})", BOLD + color))
            
            for i, issue in enumerate(severity_issues, 1):
                issue_type = issue.get("type", "Unknown")
                line = issue.get("line", "?")
                description = issue.get("description", "No description")
                suggestion = issue.get("suggestion", "No suggestion")
                
                output.append(colorize(f"#### {i}. {issue_type} (Line {line})", BOLD + color))
                output.append(colorize("**Description:**", BOLD) + f" {description}")
                output.append(colorize("**Suggestion:**", BOLD) + f" {suggestion}")
                output.append("")
    
    return "\n".join(output)