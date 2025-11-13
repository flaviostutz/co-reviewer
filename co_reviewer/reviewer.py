"""Main reviewer orchestrator."""

import logging

from co_reviewer.config import Settings, get_settings
from co_reviewer.git_scanner import GitScanner
from co_reviewer.models import CodeReview, ReviewRequest
from co_reviewer.review_agent import ReviewAgent

logger = logging.getLogger(__name__)


class CoReviewer:
    """Main code reviewer orchestrator."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize co-reviewer.

        Args:
            settings: Application settings (optional)

        """
        self.settings = settings or get_settings()
        self.review_agent = ReviewAgent(self.settings)

    def review(self, request: ReviewRequest) -> CodeReview:
        """Perform code review.

        Args:
            request: Review request

        Returns:
            CodeReview object with results

        """
        logger.info("Starting review for workspace: %s", request.workspace_path)

        # Initialize git scanner
        scanner = GitScanner(request.workspace_path, self.settings)

        # Get current branch if not specified
        current_branch = request.current_branch or scanner.get_current_branch()
        logger.info("Reviewing changes from %s to %s", request.base_branch, current_branch)

        # Get changes
        changes = scanner.get_changes(
            base_branch=request.base_branch,
            current_ref=request.current_branch,
        )

        if not changes:
            logger.info("No changes found")
            return CodeReview(
                summary="No changes detected between branches",
                files_reviewed=0,
                total_changes={"additions": 0, "deletions": 0},
                comments=[],
                positive_feedback=["No changes to review"],
                overall_assessment="no changes",
                metadata={
                    "base_branch": request.base_branch,
                    "current_branch": current_branch,
                },
            )

        # Perform review
        logger.info("Reviewing %d changed files", len(changes))
        review = self.review_agent.review_changes(
            changes=changes,
            custom_instructions=request.custom_instructions,
            focus_areas=request.focus_areas,
        )

        # Add metadata
        review.metadata.update(
            {
                "base_branch": request.base_branch,
                "current_branch": current_branch,
                "workspace_path": str(request.workspace_path),
            }
        )

        logger.info("Review completed: %s", review.overall_assessment)
        return review


def create_reviewer(settings: Settings | None = None) -> CoReviewer:
    """Factory function to create reviewer instance.

    Args:
        settings: Application settings (optional)

    Returns:
        CoReviewer instance

    """
    return CoReviewer(settings)
