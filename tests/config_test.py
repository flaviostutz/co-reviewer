"""Tests for configuration."""

from co_reviewer.config import Settings


def test_settings_defaults() -> None:
    """Test default settings."""
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
    )

    assert settings.azure_openai_deployment == "gpt-4o-mini"
    assert settings.llm_temperature == 0.2
    assert settings.default_base_branch == "main"
    assert settings.max_files_per_review == 20


def test_settings_custom() -> None:
    """Test custom settings."""
    settings = Settings(
        azure_openai_api_key="test-key",
        azure_openai_endpoint="https://test.openai.azure.com/",
        azure_openai_deployment="gpt-4o",
        llm_temperature=0.5,
        default_base_branch="develop",
    )

    assert settings.azure_openai_deployment == "gpt-4o"
    assert settings.llm_temperature == 0.5
    assert settings.default_base_branch == "develop"
