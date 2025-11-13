"""Data models for co-reviewer."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FileChangeType(str, Enum):
    """Type of file change."""

    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class ReviewSeverity(str, Enum):
    """Severity level of review comment."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class FileChange(BaseModel):
    """Represents a file change in git."""

    file_path: str = Field(description="Path to the changed file")
    change_type: FileChangeType = Field(description="Type of change")
    additions: int = Field(default=0, description="Number of lines added")
    deletions: int = Field(default=0, description="Number of lines deleted")
    diff: str = Field(description="Git diff content")
    old_path: str | None = Field(default=None, description="Old path for renamed files")


class ReviewComment(BaseModel):
    """A review comment for a code change."""

    file_path: str = Field(description="Path to the file")
    line_number: int | None = Field(default=None, description="Line number for the comment")
    severity: ReviewSeverity = Field(description="Severity of the issue")
    category: str = Field(description="Category of the review (e.g., 'code quality', 'bug risk')")
    message: str = Field(description="The review comment message")
    suggestion: str | None = Field(default=None, description="Suggested fix or improvement")


class CodeReview(BaseModel):
    """Complete code review result."""

    summary: str = Field(description="Overall summary of the review")
    files_reviewed: int = Field(description="Number of files reviewed")
    total_changes: dict[str, int] = Field(description="Total additions and deletions")
    comments: list[ReviewComment] = Field(
        default_factory=list, description="List of review comments"
    )
    positive_feedback: list[str] = Field(
        default_factory=list, description="Positive aspects of the changes"
    )
    overall_assessment: str = Field(
        description="Overall assessment (e.g., 'approved', 'needs work', 'critical issues')"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ReviewRequest(BaseModel):
    """Request for code review."""

    workspace_path: str = Field(description="Path to git workspace")
    base_branch: str = Field(default="main", description="Base branch to compare against")
    current_branch: str | None = Field(
        default=None, description="Current branch (defaults to HEAD)"
    )
    custom_instructions: str | None = Field(default=None, description="Custom review instructions")
    focus_areas: list[str] = Field(
        default_factory=list,
        description="Specific areas to focus on (e.g., 'security', 'performance')",
    )
