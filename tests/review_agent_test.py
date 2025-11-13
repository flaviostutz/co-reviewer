"""Tests for review agent."""

from unittest.mock import MagicMock, patch

import pytest

from co_reviewer.config import Settings
from co_reviewer.models import CodeReview, FileChange, FileChangeType, ReviewSeverity
from co_reviewer.review_agent import ReviewAgent


@pytest.fixture
def settings() -> Settings:
    """Create test settings."""
    return Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )


@pytest.fixture
def mock_review() -> CodeReview:
    """Create mock code review."""
    return CodeReview(
        summary="Test review",
        files_reviewed=1,
        total_changes={"additions": 10, "deletions": 5},
        comments=[],
        severity=ReviewSeverity.INFO,
        overall_assessment="Good work",
    )


@patch("co_reviewer.review_agent.AzureChatOpenAI")
def test_review_agent_init(mock_llm: MagicMock, settings: Settings) -> None:
    """Test review agent initialization."""
    mock_llm.return_value = MagicMock()
    agent = ReviewAgent(settings)
    assert agent.settings == settings
    assert agent.llm is not None


@patch("co_reviewer.review_agent.AzureChatOpenAI")
def test_prepare_review_context(mock_llm: MagicMock, settings: Settings) -> None:
    """Test review context preparation."""
    mock_llm.return_value = MagicMock()
    agent = ReviewAgent(settings)

    changes = [
        FileChange(
            file_path="test.py",
            change_type=FileChangeType.MODIFIED,
            additions=10,
            deletions=5,
            diff="- old\n+ new",
            old_path=None,
        )
    ]

    context = agent._prepare_review_context(  # noqa: SLF001
        changes,
        custom_instructions="Be careful",
        focus_areas=["security"],
    )

    assert context["num_files"] == 1
    assert context["total_additions"] == 10
    assert context["total_deletions"] == 5
    assert "security" in context["focus_areas"]
    assert "Be careful" in context["custom_instructions"]


@patch("co_reviewer.review_agent.AzureChatOpenAI")
def test_create_error_review(mock_llm: MagicMock, settings: Settings) -> None:
    """Test error review creation."""
    mock_llm.return_value = MagicMock()
    agent = ReviewAgent(settings)

    changes = [
        FileChange(
            file_path="test.py",
            change_type=FileChangeType.MODIFIED,
            additions=10,
            deletions=5,
            diff="- old\n+ new",
            old_path=None,
        )
    ]

    review = agent._create_error_review(changes, "Test error")  # noqa: SLF001

    assert "Test error" in review.summary
    assert review.files_reviewed == 1
    assert review.total_changes["additions"] == 10
