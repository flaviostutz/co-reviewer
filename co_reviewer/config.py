"""Configuration management for co-reviewer."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Azure OpenAI Configuration
    azure_openai_api_key: str = Field(default="", description="Azure OpenAI API key")
    azure_openai_endpoint: str = Field(default="", description="Azure OpenAI endpoint URL")
    azure_openai_deployment: str = Field(
        default="gpt-4o-mini", description="Azure OpenAI deployment name"
    )
    azure_openai_api_version: str = Field(
        default="2024-08-01-preview", description="Azure OpenAI API version"
    )
    llm_temperature: float = Field(default=0.2, description="Temperature for LLM")

    # Git Configuration
    default_base_branch: str = Field(default="main", description="Default base branch")
    max_diff_size: int = Field(default=10000, description="Maximum diff size in characters")

    # Review Configuration
    max_files_per_review: int = Field(
        default=20, description="Maximum files to review in one batch"
    )
    include_context_lines: int = Field(
        default=3, description="Number of context lines to include in diffs"
    )

    @property
    def workspace_root(self) -> Path:
        """Get workspace root directory."""
        return Path.cwd()


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
