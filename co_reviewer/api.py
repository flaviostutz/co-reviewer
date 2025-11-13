"""FastAPI server for co-reviewer."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from co_reviewer.config import get_settings
from co_reviewer.models import CodeReview, ReviewRequest
from co_reviewer.reviewer import CoReviewer, create_reviewer

logger = logging.getLogger(__name__)

# Global reviewer instance
reviewer: CoReviewer | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    global reviewer  # noqa: PLW0603
    settings = get_settings()
    reviewer = create_reviewer(settings)
    logger.info("Co-Reviewer API started")
    yield
    logger.info("Co-Reviewer API shutting down")


app = FastAPI(
    title="Co-Reviewer API",
    description="AI-powered code review assistant",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Co-Reviewer API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/review")
async def review_code(request: ReviewRequest) -> CodeReview:
    """Review code changes endpoint.

    Args:
        request: Review request

    Returns:
        Code review results

    """
    if reviewer is None:
        raise HTTPException(status_code=500, detail="Reviewer not initialized")

    try:
        logger.info("Received review request for workspace: %s", request.workspace_path)
        return reviewer.review(request)
    except ValueError as e:
        logger.exception("Invalid request")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Review failed")
        raise HTTPException(status_code=500, detail=f"Review failed: {e!s}") from e
