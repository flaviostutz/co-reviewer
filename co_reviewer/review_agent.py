"""LangChain-based review agent for code analysis."""

import logging
from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr

from co_reviewer.config import Settings
from co_reviewer.models import CodeReview, FileChange, ReviewComment, ReviewSeverity

logger = logging.getLogger(__name__)


class ReviewAgent:
    """AI agent for code review using LangChain."""

    def __init__(self, settings: Settings) -> None:
        """Initialize review agent.

        Args:
            settings: Application settings

        """
        self.settings = settings
        self.llm = self._init_llm()

    def _init_llm(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI LLM."""
        return AzureChatOpenAI(
            azure_deployment=self.settings.azure_openai_deployment,
            api_version=self.settings.azure_openai_api_version,
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_key=SecretStr(self.settings.azure_openai_api_key),
            temperature=self.settings.llm_temperature,
        )

    def review_changes(
        self,
        changes: list[FileChange],
        custom_instructions: str | None = None,
        focus_areas: list[str] | None = None,
    ) -> CodeReview:
        """Review code changes and provide feedback.

        Args:
            changes: List of file changes to review
            custom_instructions: Custom review instructions
            focus_areas: Specific areas to focus on

        Returns:
            CodeReview object with review results

        """
        if not changes:
            return CodeReview(
                summary="No changes to review",
                files_reviewed=0,
                total_changes={"additions": 0, "deletions": 0},
                comments=[],
                positive_feedback=[],
                overall_assessment="no changes",
                metadata={},
            )

        # Limit number of files
        if len(changes) > self.settings.max_files_per_review:
            logger.warning(
                f"Too many files ({len(changes)}), limiting to {self.settings.max_files_per_review}"
            )
            changes = changes[: self.settings.max_files_per_review]

        # Prepare context
        review_context = self._prepare_review_context(changes, custom_instructions, focus_areas)

        # Run review
        try:
            return self._run_review_chain(review_context)
        except Exception as e:
            logger.exception("Review failed")
            return self._create_error_review(changes, str(e))

    def _prepare_review_context(
        self,
        changes: list[FileChange],
        custom_instructions: str | None,
        focus_areas: list[str] | None,
    ) -> dict[str, Any]:
        """Prepare context for review."""
        total_additions = sum(c.additions for c in changes)
        total_deletions = sum(c.deletions for c in changes)

        # Format changes for review
        changes_text = []
        for change in changes:
            change_info = f"""
File: {change.file_path}
Change Type: {change.change_type.value}
Additions: +{change.additions}, Deletions: -{change.deletions}
{f"Old Path: {change.old_path}" if change.old_path else ""}

Diff:
{change.diff}
---
"""
            changes_text.append(change_info.strip())

        return {
            "num_files": len(changes),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "changes": "\n\n".join(changes_text),
            "custom_instructions": custom_instructions or "None",
            "focus_areas": ", ".join(focus_areas) if focus_areas else "General code quality",
        }

    def _run_review_chain(self, context: dict[str, Any]) -> CodeReview:
        """Run LangChain review chain."""
        # Define output parser
        parser = PydanticOutputParser(pydantic_object=CodeReview)

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are an expert code reviewer with deep knowledge of "
                        "software engineering best practices, security, performance "
                        "optimization, and code quality. Your goal is to provide "
                        "constructive, actionable feedback on code changes."
                    ),
                ),
                (
                    "user",
                    (
                        "Review the following code changes and provide "
                        "comprehensive feedback.\n\n"
                        "Number of Files: {num_files}\n"
                        "Total Changes: +{total_additions} -{total_deletions}\n"
                        "Focus Areas: {focus_areas}\n"
                        "Custom Instructions: {custom_instructions}\n\n"
                        "CODE CHANGES:\n"
                        "{changes}\n\n"
                        "Please analyze these changes and provide:\n"
                        "1. A summary of what changed\n"
                        "2. Specific review comments for issues or improvements "
                        "(categorized by severity: info, warning, error, critical)\n"
                        "3. Positive feedback on good practices\n"
                        "4. Overall assessment\n\n"
                        "Focus on:\n"
                        "- Code quality and maintainability\n"
                        "- Potential bugs or logical errors\n"
                        "- Security vulnerabilities\n"
                        "- Performance issues\n"
                        "- Best practices and conventions\n"
                        "- Testing considerations\n"
                        "- Documentation needs\n\n"
                        "{format_instructions}\n\n"
                        "Provide your review in the specified JSON format."
                    ),
                ),
            ]
        )

        # Create chain
        chain: Runnable[Any, CodeReview] = (
            {"format_instructions": lambda _: parser.get_format_instructions()}
            | RunnablePassthrough()
            | prompt
            | self.llm
            | parser
        )

        # Run chain
        return chain.invoke(context)

    def _create_error_review(self, changes: list[FileChange], error_msg: str) -> CodeReview:
        """Create error review when review fails."""
        total_additions = sum(c.additions for c in changes)
        total_deletions = sum(c.deletions for c in changes)

        return CodeReview(
            summary=f"Review failed with error: {error_msg}",
            files_reviewed=len(changes),
            total_changes={
                "additions": total_additions,
                "deletions": total_deletions,
            },
            comments=[
                ReviewComment(
                    file_path="N/A",
                    severity=ReviewSeverity.ERROR,
                    category="system",
                    message=f"Review process failed: {error_msg}",
                )
            ],
            positive_feedback=[],
            overall_assessment="error",
            metadata={"error": error_msg},
        )
