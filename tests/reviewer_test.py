"""Tests for reviewer."""

from pathlib import Path

from git import Repo

from co_reviewer.config import Settings
from co_reviewer.models import ReviewRequest
from co_reviewer.reviewer import CoReviewer


def test_reviewer_init() -> None:
    """Test reviewer initialization."""
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )
    reviewer = CoReviewer(settings)

    assert reviewer.settings == settings
    assert reviewer.review_agent is not None


def test_review_no_changes(tmp_path: Path) -> None:
    """Test review with no changes."""
    # Create a git repo
    repo = Repo.init(tmp_path)

    # Create initial commit
    test_file = tmp_path / "test.txt"
    test_file.write_text("Initial content")
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Initialize reviewer
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )
    reviewer = CoReviewer(settings)

    # Create review request
    main_branch = "main" if "main" in [h.name for h in repo.heads] else "master"
    request = ReviewRequest(
        workspace_path=str(tmp_path),
        base_branch=main_branch,
    )

    # Perform review
    result = reviewer.review(request)

    assert result.files_reviewed == 0
    assert result.overall_assessment == "no changes"
    assert result.total_changes["additions"] == 0
    assert result.total_changes["deletions"] == 0
