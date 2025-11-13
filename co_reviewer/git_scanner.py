"""Git repository scanner for detecting code changes."""

import logging
from pathlib import Path

import git
from git import Repo

from co_reviewer.config import Settings
from co_reviewer.models import FileChange, FileChangeType

logger = logging.getLogger(__name__)


class GitScanner:
    """Scans git repository for code changes."""

    def __init__(self, workspace_path: str | Path, settings: Settings) -> None:
        """Initialize git scanner.

        Args:
            workspace_path: Path to git workspace
            settings: Application settings

        """
        self.workspace_path = Path(workspace_path)
        self.settings = settings
        self.repo = self._init_repo()

    def _init_repo(self) -> Repo:
        """Initialize git repository."""
        try:
            repo = Repo(self.workspace_path)
            if repo.bare:
                raise ValueError(f"Repository at {self.workspace_path} is bare")
            return repo
        except git.exc.InvalidGitRepositoryError as e:
            raise ValueError(f"Not a valid git repository: {self.workspace_path}") from e

    def get_current_branch(self) -> str:
        """Get current branch name."""
        if self.repo.head.is_detached:
            return self.repo.head.commit.hexsha[:8]
        return str(self.repo.active_branch)

    def get_changes(
        self, base_branch: str = "main", current_ref: str | None = None
    ) -> list[FileChange]:
        """Get file changes between branches.

        Args:
            base_branch: Base branch to compare against
            current_ref: Current ref (branch/commit), defaults to HEAD

        Returns:
            List of file changes

        """
        if current_ref is None:
            current_ref = "HEAD"

        try:
            # Get the diff between base branch and current ref
            base_commit = self.repo.commit(base_branch)
            current_commit = self.repo.commit(current_ref)

            diffs = base_commit.diff(
                current_commit, create_patch=True, unified=self.settings.include_context_lines
            )

            changes: list[FileChange] = []
            for diff in diffs:
                change = self._parse_diff(diff)
                if change:
                    changes.append(change)

            logger.info(
                f"Found {len(changes)} file changes between {base_branch} and {current_ref}"
            )
            return changes

        except git.exc.GitCommandError as e:
            raise ValueError(f"Failed to get git diff: {e}") from e

    def _parse_diff(self, diff: git.Diff) -> FileChange | None:
        """Parse git diff object into FileChange.

        Args:
            diff: Git diff object

        Returns:
            FileChange object or None if invalid

        """
        try:
            # Determine change type
            if diff.new_file:
                change_type = FileChangeType.ADDED
                file_path = diff.b_path or ""
                old_path = None
            elif diff.deleted_file:
                change_type = FileChangeType.DELETED
                file_path = diff.a_path or ""
                old_path = None
            elif diff.renamed_file:
                change_type = FileChangeType.RENAMED
                file_path = diff.b_path or ""
                old_path = diff.a_path
            else:
                change_type = FileChangeType.MODIFIED
                file_path = diff.b_path or diff.a_path or ""
                old_path = None

            # Get diff content
            diff_text = ""
            if diff.diff:
                try:
                    if isinstance(diff.diff, bytes):
                        diff_text = diff.diff.decode("utf-8", errors="replace")
                    else:
                        diff_text = str(diff.diff)
                except Exception:
                    logger.warning("Failed to decode diff for %s", file_path)
                    diff_text = str(diff.diff)

            # Limit diff size
            if len(diff_text) > self.settings.max_diff_size:
                diff_text = (
                    diff_text[: self.settings.max_diff_size]
                    + f"\n... (truncated, total size: {len(diff_text)} chars)"
                )

            # Count additions and deletions from diff stats
            additions = 0
            deletions = 0
            if hasattr(diff, "stats") and diff.stats:
                additions = diff.stats.get("insertions", 0)
                deletions = diff.stats.get("deletions", 0)
            else:
                # Fallback: count from diff text
                for line in diff_text.split("\n"):
                    if line.startswith("+") and not line.startswith("+++"):
                        additions += 1
                    elif line.startswith("-") and not line.startswith("---"):
                        deletions += 1

            return FileChange(
                file_path=file_path,
                change_type=change_type,
                additions=additions,
                deletions=deletions,
                diff=diff_text,
                old_path=old_path,
            )
        except Exception:
            logger.exception("Error parsing diff")
            return None

    def get_file_content(self, file_path: str, ref: str = "HEAD") -> str:
        """Get file content at specific ref.

        Args:
            file_path: Path to file
            ref: Git ref (branch/commit)

        Returns:
            File content as string

        """
        try:
            commit = self.repo.commit(ref)
            blob = commit.tree / file_path
            content_bytes = blob.data_stream.read()
            if isinstance(content_bytes, bytes):
                return content_bytes.decode("utf-8", errors="replace")
            return str(content_bytes)
        except Exception:
            logger.exception("Failed to get file content for %s at %s", file_path, ref)
            return ""
