"""Tests for git scanner."""

from pathlib import Path

import pytest
from git import Repo

from co_reviewer.config import Settings
from co_reviewer.git_scanner import GitScanner
from co_reviewer.models import FileChangeType


def test_git_scanner_init(tmp_path: Path) -> None:
    """Test git scanner initialization."""
    # Create a git repo
    repo = Repo.init(tmp_path)

    # Create initial commit
    test_file = tmp_path / "test.txt"
    test_file.write_text("Initial content")
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Initialize scanner
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )
    scanner = GitScanner(tmp_path, settings)

    assert scanner.repo is not None
    assert not scanner.repo.bare


def test_git_scanner_invalid_repo(tmp_path: Path) -> None:
    """Test git scanner with invalid repo."""
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )

    with pytest.raises(ValueError, match="Not a valid git repository"):
        GitScanner(tmp_path, settings)


def test_get_current_branch(tmp_path: Path) -> None:
    """Test getting current branch."""
    # Create a git repo
    repo = Repo.init(tmp_path)

    # Create initial commit
    test_file = tmp_path / "test.txt"
    test_file.write_text("Initial content")
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Initialize scanner
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )
    scanner = GitScanner(tmp_path, settings)

    current_branch = scanner.get_current_branch()
    assert current_branch in ["main", "master"]  # Depends on git config


def test_get_changes(tmp_path: Path) -> None:
    """Test getting file changes."""
    # Create a git repo with changes
    repo = Repo.init(tmp_path)

    # Create initial commit on main
    test_file = tmp_path / "test.txt"
    test_file.write_text("Initial content")
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Create a new branch
    repo.create_head("feature")
    repo.heads.feature.checkout()

    # Make changes
    test_file.write_text("Updated content")
    repo.index.add([str(test_file)])
    repo.index.commit("Update test file")

    new_file = tmp_path / "new.txt"
    new_file.write_text("New file")
    repo.index.add([str(new_file)])
    repo.index.commit("Add new file")

    # Initialize scanner
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )
    scanner = GitScanner(tmp_path, settings)

    # Get changes
    main_branch = "main" if "main" in [h.name for h in repo.heads] else "master"
    changes = scanner.get_changes(base_branch=main_branch)

    assert len(changes) == 2

    # Check modified file
    modified = next(c for c in changes if c.file_path == "test.txt")
    assert modified.change_type == FileChangeType.MODIFIED
    assert modified.additions > 0
    assert modified.deletions > 0

    # Check new file
    added = next(c for c in changes if c.file_path == "new.txt")
    assert added.change_type == FileChangeType.ADDED
    assert added.additions > 0


def test_get_current_branch_detached(tmp_path: Path) -> None:
    """Test getting current branch in detached HEAD state."""
    # Create a git repo
    repo = Repo.init(tmp_path)

    # Create initial commit
    test_file = tmp_path / "test.txt"
    test_file.write_text("Initial content")
    repo.index.add([str(test_file)])
    commit = repo.index.commit("Initial commit")

    # Initialize scanner
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )
    scanner = GitScanner(tmp_path, settings)

    # Checkout detached HEAD
    repo.head.reference = commit

    # Get current branch - should return commit SHA
    current_branch = scanner.get_current_branch()
    assert current_branch != ""
    assert len(current_branch) == 8  # First 8 chars of SHA


def test_get_file_content(tmp_path: Path) -> None:
    """Test getting file content at specific commit."""
    # Create a git repo
    repo = Repo.init(tmp_path)

    # Create initial commit
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    repo.index.add([str(test_file)])
    repo.index.commit("Initial commit")

    # Initialize scanner
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )
    scanner = GitScanner(tmp_path, settings)

    # Get file content
    main_branch = "main" if "main" in [h.name for h in repo.heads] else "master"
    content = scanner.get_file_content("test.txt", main_branch)

    assert content == "Test content"
