"""Command-line interface for co-reviewer."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from co_reviewer import __version__
from co_reviewer.config import get_settings
from co_reviewer.models import CodeReview, ReviewRequest, ReviewSeverity
from co_reviewer.reviewer import create_reviewer

app = typer.Typer(help="Co-Reviewer: AI-powered code review assistant")
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@app.command()
def review(  # noqa: PLR0913
    workspace: Annotated[
        Path | None,
        typer.Argument(
            help="Path to git workspace",
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ] = None,
    base_branch: Annotated[
        str, typer.Option("--base", "-b", help="Base branch to compare against")
    ] = "main",
    current_branch: Annotated[
        str | None, typer.Option("--current", "-c", help="Current branch (defaults to HEAD)")
    ] = None,
    instructions: Annotated[
        str | None, typer.Option("--instructions", "-i", help="Custom review instructions")
    ] = None,
    focus: Annotated[
        list[str] | None,
        typer.Option("--focus", "-f", help="Focus areas (can be specified multiple times)"),
    ] = None,
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Output file for JSON results")
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,  # noqa: FBT002
) -> None:
    """Review code changes in a git workspace."""
    if workspace is None:
        workspace = Path.cwd()
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Create review request
        request = ReviewRequest(
            workspace_path=str(workspace),
            base_branch=base_branch,
            current_branch=current_branch,
            custom_instructions=instructions,
            focus_areas=focus or [],
        )

        console.print(f"\n[bold blue]🔍 Reviewing code changes in:[/bold blue] {workspace}")
        console.print(f"[dim]Base branch: {base_branch}[/dim]")
        if current_branch:
            console.print(f"[dim]Current branch: {current_branch}[/dim]")

        # Perform review
        settings = get_settings()
        reviewer = create_reviewer(settings)

        with console.status("[bold green]Analyzing changes..."):
            review_result = reviewer.review(request)

        # Display results
        _display_review(review_result)

        # Save to file if requested
        if output:
            output.write_text(review_result.model_dump_json(indent=2))
            console.print(f"\n[green]✓[/green] Results saved to: {output}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Review failed")
        raise typer.Exit(code=1) from e


def _display_review(review: CodeReview) -> None:
    """Display review results in console."""
    # Summary panel
    console.print(
        Panel(
            f"[bold]{review.summary}[/bold]\n\n"
            f"Files Reviewed: {review.files_reviewed}\n"
            f"Total Changes: [green]+{review.total_changes.get('additions', 0)}[/green] "
            f"[red]-{review.total_changes.get('deletions', 0)}[/red]\n"
            f"Assessment: [bold]{review.overall_assessment.upper()}[/bold]",
            title="📋 Review Summary",
            border_style="blue",
        )
    )

    # Comments table
    if review.comments:
        console.print("\n[bold]📝 Review Comments:[/bold]\n")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan", no_wrap=False)
        table.add_column("Line", justify="right", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Category", style="blue")
        table.add_column("Message", style="white")

        for comment in review.comments:
            severity_style = {
                ReviewSeverity.INFO: "blue",
                ReviewSeverity.WARNING: "yellow",
                ReviewSeverity.ERROR: "red",
                ReviewSeverity.CRITICAL: "bold red",
            }.get(comment.severity, "white")

            table.add_row(
                comment.file_path,
                str(comment.line_number) if comment.line_number else "N/A",
                f"[{severity_style}]{comment.severity.value.upper()}[/{severity_style}]",
                comment.category,
                comment.message,
            )

        console.print(table)

        # Show suggestions
        suggestions = [c for c in review.comments if c.suggestion]
        if suggestions:
            console.print("\n[bold]💡 Suggestions:[/bold]\n")
            for i, comment in enumerate(suggestions, 1):
                console.print(
                    f"{i}. [cyan]{comment.file_path}[/cyan] (Line {comment.line_number or 'N/A'})"
                )
                console.print(f"   {comment.suggestion}\n")

    # Positive feedback
    if review.positive_feedback:
        console.print("\n[bold green]✓ Positive Feedback:[/bold green]\n")
        for feedback in review.positive_feedback:
            console.print(f"  • {feedback}")


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"Co-Reviewer version: [bold]{__version__}[/bold]")


if __name__ == "__main__":
    app()
