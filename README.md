# Code Reviewer

A CLI tool that reviews code in your project, identifies issues, and suggests fixes.

## Features

- Analyzes code for logical errors, runtime errors, and compilation errors
- Identifies performance issues and security vulnerabilities
- Suggests fixes for each identified issue
- Supports multiple programming languages
- Uses OpenAI models to generate high-quality reviews

## Installation

```bash
# Clone the repository
git clone https://github.com/roulpriya/code-reviewer.git
cd code-reviewer

# Install using pip
pip install -e .

# Or install using Poetry
poetry install
```

## Configuration

Before using the tool, you need to configure your OpenAI API key:

```bash
code_reviewer config --api-key YOUR_OPENAI_API_KEY
```

You can also configure other settings:

```bash
code_reviewer config --model gpt-4 --max-tokens 1000 --temperature 0.3
```

## Usage

### Review Current Project

```bash
code_reviewer review
```

### Review Specific Directory

```bash
code_reviewer review /path/to/your/project
```

### Save Review Results to File

```bash
code_reviewer review --output review_results.json
```

## Supported Languages

- Python
- JavaScript/TypeScript
- Java
- C/C++
- Go
- Rust
- Ruby
- PHP
- Swift
- Kotlin
- C#

## Configuration Options

- `--api-key`: Your OpenAI API key
- `--model`: OpenAI model to use (default: gpt-4)
- `--max-tokens`: Maximum tokens for each API request
- `--temperature`: Temperature for the API request (0.0-1.0)
- `--max-file-size`: Maximum file size in bytes to review
- `--max-files`: Maximum number of files to review

## License

MIT
