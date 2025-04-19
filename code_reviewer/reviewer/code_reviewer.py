#!/usr/bin/env python3

import json
import logging
import os
import re
from typing import Dict, Any, Optional

import openai

from code_reviewer.config import Config
from code_reviewer.tools import tree, read_file_content

logger = logging.getLogger("code-reviewer")


class CodeReviewer:
    """CLI application that reviews code in a project directory."""

    def __init__(self, project_path: str):
        """Initialize the code reviewer.

        Args:
            project_path: Path to the project directory to review
            config_path: Optional path to the config file (default: ~/.code_reviewer_config.json)
        """
        self.project_path = os.path.abspath(project_path)
        self.config_path = os.path.expanduser("~/.code_reviewer_config.json")
        self.config_manager = Config(self.config_path)
        self.openai_client = self._init_openai_client()

    def _init_openai_client(self) -> Any:
        """Initialize the OpenAI client using the API key from config."""
        api_key = self.config_manager.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI API key not found in config or environment variables.")
            logger.error("Please run: code_reviewer config --api-key YOUR_API_KEY")
            raise ValueError("OpenAI API key not found")

        return openai.OpenAI(api_key=api_key, base_url=self.config_manager.get("endpoint"))

    def review_code(self, file_path: str) -> Dict[str, Any]:
        """Review code using the OpenAI API."""
        prompt = """
        You are an expert code reviewer. Review code and identify:
        1. Logical errors or bugs
        2. Potential runtime errors
        3. Compilation errors
        4. Performance issues
        5. Security vulnerabilities
        6. Best practice violations
        7. Code style issues
        
        Use provided tools to explore the current directory and review files
        one by one.
        
        You have access to `tree` and `read_file` tools.
        
        Provide a detailed analysis with line numbers for each issue. Focus on the most critical problems first.
        IMPORTANT: Format your response as JSON with the following structure:
        {{
            "issues": [
                {{
                    "type": "<issue_type>",
                    "line": <line_number>,
                    "description": "<detailed_description>",
                    "severity": "<high|medium|low>",
                    "suggestion": "<suggested_fix>"
                }}
            ],
            "summary": "<overall_code_quality_assessment>",
            "file": "<file>"
        }}
        """
        tools = [{
            "type": "function",
            "function": {
                "name": "tree",
                "description": "Get the file tree of the project directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The root directory of the project."
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the content of a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file."
                        }
                    },
                    "required": ["file_path"]
                }
            }
        }]

        messages = [{"role": "system",
                     "content": "You are a code review assistant that provides detailed and actionable feedback."},
                    {"role": "user", "content": prompt}]

        loop = True
        while loop:
            try:
                # Log request details
                logger.debug(f"Sending request to OpenAI with model: {self.config_manager.get('model')}")

                # # Convert messages to a serializable format
                # serializable_messages = []
                # for msg in messages:
                #     if isinstance(msg, dict):
                #         serializable_messages.append(msg)
                #     else:
                #         # For object types like ChatCompletionMessage
                #         serializable_messages.append({
                #             "role": msg.role,
                #             "content": msg.content if msg.content else None,
                #             "tool_call_id": getattr(msg, "tool_call_id", None),
                #             "tool_calls": getattr(msg, "tool_calls", None)
                #         })
                #
                # logger.debug(f"Request messages: {json.dumps(serializable_messages)}")
                # logger.debug(f"Request tools: {json.dumps(tools)}")

                response = self.openai_client.chat.completions.create(
                    model=self.config_manager.get("model"),
                    messages=messages,
                    max_tokens=self.config_manager.get("max_tokens"),
                    temperature=self.config_manager.get("temperature"),
                    tools=tools
                )

                # Log response as a dict to make it serializable
                try:
                    response_dict = response.model_dump()
                    logger.debug(f"OpenAI response: {json.dumps(response_dict)}")
                except Exception as e:
                    logger.debug(f"Could not serialize full response: {str(e)}")
                    logger.debug(f"Response model: {response.model}")
                    logger.debug(f"Response choices count: {len(response.choices)}")

                messages.append(response.choices[0].message)
                tool_call_results = []

                calls = response.choices[0].message.tool_calls
                if calls:
                    logger.debug(f"Tool calls detected: {len(calls)}")
                    for tool_call in calls:
                        # Log tool call details safely
                        try:
                            tool_call_info = {
                                "id": tool_call.id,
                                "type": tool_call.type,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                            logger.debug(f"Tool call details: {json.dumps(tool_call_info)}")
                        except Exception as e:
                            logger.debug(f"Could not serialize tool call: {str(e)}")

                        logger.debug(f"Processing tool call: {tool_call.function.name} with id: {tool_call.id}")
                        args = json.loads(tool_call.function.arguments)
                        logger.debug(f"Tool arguments: {json.dumps(args)}")

                        tool_result = "TOOL NOT FOUND"
                        if tool_call.function.name == "tree":
                            logger.debug(f"Calling tree function with args: {args}")
                            tool_result = tree(**args)
                        elif tool_call.function.name == "read_file":
                            logger.debug(f"Calling read_file function with args: {args}")
                            tool_result = read_file_content(**args)
                        else:
                            logger.warning(f"Unknown tool called: {tool_call.function.name}")

                        logger.debug(f"Tool result summary (truncated): {str(tool_result)[:100]}...")

                        tool_call_results.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result)
                        })

                    # Add tool results to messages
                    messages.extend(tool_call_results)
                else:
                    loop = False

                try:
                    # Parse the JSON response
                    result = response.choices[0].message.content
                    logger.debug(f"Attempting to parse JSON result: {result[:200]}...")
                    json_result = json.loads(result)
                    logger.debug(f"Successfully parsed JSON with {len(json_result.get('issues', []))} issues")
                    yield json_result
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing error: {e}")
                    logger.debug(f"Raw response content: {result}")

            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"Error reviewing {file_path}: {str(e)}")
                logger.debug(f"Full error traceback: {error_details}")

                if hasattr(e, 'response'):
                    try:
                        resp_json = e.response.json()
                        logger.error(f"API error response: {json.dumps(resp_json)}")
                    except (AttributeError, json.JSONDecodeError):
                        if hasattr(e, 'response') and hasattr(e.response, 'text'):
                            logger.error(f"API error text: {e.response.text}")

                return {
                    "issues": [],
                    "summary": f"Error reviewing file: {str(e)}"
                }

    def review_project(self) -> Dict[str, Any]:
        """Review all code files in the project."""
        logger.info(f"Starting code review of {self.project_path}")

        review_results = {}
        all_issues = []

        for review in self.review_code(self.project_path):
            # Store the review result with file path as key
            file_path = review.get("file")
            if file_path:
                review_results[file_path] = review
                
                # Add file path to each issue and collect all issues
                for issue in review.get("issues", []):
                    issue["file"] = file_path
                    all_issues.append(issue)

        # Sort issues by severity
        severity_rank = {"high": 0, "medium": 1, "low": 2}
        all_issues.sort(key=lambda x: severity_rank.get(x.get("severity", "low"), 3))

        return {
            "project": self.project_path,
            "results": review_results,
            "issues": all_issues,
            "stats": {
                "files_reviewed": len(review_results),
                "total_issues": len(all_issues),
                "high_severity": sum(1 for i in all_issues if i.get("severity") == "high"),
                "medium_severity": sum(1 for i in all_issues if i.get("severity") == "medium"),
                "low_severity": sum(1 for i in all_issues if i.get("severity") == "low"),
            }
        }

    def display_results(self, results: Dict[str, Any]) -> None:
        """Display the review results in the terminal."""
        issues = results.get("issues", [])
        stats = results.get("stats", {})

        print("\n" + "=" * 80)
        print(f"CODE REVIEW SUMMARY: {self.project_path}")
        print("=" * 80)
        print(f"Files reviewed: {stats.get('files_reviewed', 0)}")
        print(f"Total issues found: {stats.get('total_issues', 0)}")
        print(f"  High severity: {stats.get('high_severity', 0)}")
        print(f"  Medium severity: {stats.get('medium_severity', 0)}")
        print(f"  Low severity: {stats.get('low_severity', 0)}")
        print("=" * 80 + "\n")

        if not issues:
            print("No issues found in the reviewed code.")
            return

        print("ISSUES BY SEVERITY:\n")

        severity_headers = {
            "high": "HIGH SEVERITY ISSUES",
            "medium": "MEDIUM SEVERITY ISSUES",
            "low": "LOW SEVERITY ISSUES"
        }

        for severity in ["high", "medium", "low"]:
            severity_issues = [i for i in issues if i.get("severity") == severity]

            if severity_issues:
                print(f"\n{severity_headers[severity]}:")
                print("-" * len(severity_headers[severity]) + "\n")

                for idx, issue in enumerate(severity_issues, 1):
                    file_path = issue.get("file", "")
                    line_num = issue.get("line", "")
                    issue_type = issue.get("type", "Unknown")
                    description = issue.get("description", "")
                    suggestion = issue.get("suggestion", "")

                    print(f"{idx}. {file_path}:{line_num} - {issue_type}")
                    print(f"   Description: {description}")
                    print(f"   Suggestion: {suggestion}\n")
