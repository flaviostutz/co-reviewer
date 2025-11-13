"""Tests for CLI."""

import pytest
from typer.testing import CliRunner

from co_reviewer.cli import app


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI runner for testing."""
    return CliRunner()


def test_review_command_help(cli_runner: CliRunner) -> None:
    """Test review command with help."""
    result = cli_runner.invoke(app, ["review", "--help"])
    assert result.exit_code == 0
    assert "Review code changes" in result.stdout


def test_app_initialization() -> None:
    """Test app initialization."""
    assert app is not None
    assert app.registered_commands
