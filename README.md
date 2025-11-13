# co-reviewer

Agentic AI system to help with code review. Can be run locally, in pipelines and receive custom instructions.

## Features

- 🤖 **AI-Powered Reviews**: Uses LangChain with Azure OpenAI for intelligent code analysis
- 🔍 **Git Integration**: Automatically detects changes between branches
- 📊 **Comprehensive Analysis**: Reviews code quality, security, performance, and best practices
- 🎯 **Customizable**: Support for custom instructions and focus areas
- 🚀 **Multiple Interfaces**: CLI, Python API, and REST API
- 📝 **Detailed Feedback**: Categorized comments with severity levels and suggestions

## Installation

### Prerequisites

- Python 3.11 or higher
- Git
- Azure OpenAI API key and endpoint

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/flaviostutz/co-reviewer.git
cd co-reviewer

# Setup and install
make setup
make install
```

### Manual Installation

```bash
pip install -e .
```

## Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

## Usage

### Command Line Interface

Review changes in current workspace:

```bash
make run
# or
uv run python -m co_reviewer.cli review
```

Review specific workspace:

```bash
uv run python -m co_reviewer.cli review /path/to/workspace
```

With custom options:

```bash
uv run python -m co_reviewer.cli review \
  --base main \
  --current feature-branch \
  --instructions "Focus on security vulnerabilities" \
  --focus security \
  --focus performance \
  --output review-results.json
```

### Python API

```python
from co_reviewer.models import ReviewRequest
from co_reviewer.reviewer import create_reviewer

# Create reviewer
reviewer = create_reviewer()

# Create review request
request = ReviewRequest(
    workspace_path="/path/to/workspace",
    base_branch="main",
    custom_instructions="Focus on type safety",
    focus_areas=["security", "performance"]
)

# Perform review
review = reviewer.review(request)

# Access results
print(f"Summary: {review.summary}")
print(f"Assessment: {review.overall_assessment}")

for comment in review.comments:
    print(f"{comment.file_path}: {comment.message}")
```

### REST API

Start the API server:

```bash
make run-server
# or
uv run uvicorn co_reviewer.api:app --reload
```

Make a review request:

```bash
curl -X POST "http://localhost:8000/review" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_path": "/path/to/workspace",
    "base_branch": "main",
    "custom_instructions": "Focus on security",
    "focus_areas": ["security", "performance"]
  }'
```

API documentation available at: http://localhost:8000/docs

## Development

### Setup Development Environment

```bash
make setup
make install
```

### Run Tests

```bash
make test
```

### Run Linters

```bash
make lint
```

### Fix Linting Issues

```bash
make lint-fix
```

### Run All Checks

```bash
make all
```

## Project Structure

```
co-reviewer/
├── co_reviewer/
│   ├── __init__.py
│   ├── api.py              # FastAPI REST API
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration management
│   ├── git_scanner.py      # Git repository scanner
│   ├── models.py           # Pydantic data models
│   ├── review_agent.py     # LangChain review agent
│   └── reviewer.py         # Main orchestrator
├── tests/
│   ├── test_config.test.py
│   ├── test_git_scanner.test.py
│   └── test_reviewer.test.py
├── .env.example
├── .gitignore
├── Makefile
├── pyproject.toml
└── README.md
```

## How It Works

1. **Git Scanning**: The `GitScanner` analyzes the git repository and extracts diffs between branches
2. **Context Preparation**: File changes are formatted with context for the AI agent
3. **AI Review**: LangChain agent processes the changes using Azure OpenAI models
4. **Structured Output**: Results are parsed into structured `CodeReview` objects
5. **Presentation**: Results are displayed via CLI, API, or returned as JSON

## Review Categories

The agent reviews code across multiple dimensions:

- **Code Quality**: Maintainability, readability, conventions
- **Security**: Vulnerabilities, injection risks, authentication issues
- **Performance**: Optimization opportunities, algorithmic complexity
- **Best Practices**: Design patterns, SOLID principles
- **Testing**: Test coverage, test quality
- **Documentation**: Comments, docstrings, README updates

## Severity Levels

- **INFO**: Informational feedback, suggestions
- **WARNING**: Minor issues that should be addressed
- **ERROR**: Significant issues that need fixing
- **CRITICAL**: Critical issues that must be fixed immediately

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please ensure all tests pass and linting is clean:

```bash
make all
```

## Roadmap

- [ ] Support for more LLM providers (standard OpenAI, Anthropic, local models, etc.)
- [ ] GitHub Actions integration
- [ ] GitLab CI/CD integration
- [ ] Incremental reviews (only review changed lines)
- [ ] Code fix suggestions with diffs
- [ ] Integration with popular code review platforms
- [ ] Custom rule definitions
- [ ] Team-specific coding standards
