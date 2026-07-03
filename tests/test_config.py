"""Tests for bot.config module."""

import pytest

from bot.config import Settings, _parse_csv, get_settings, validate_settings


def test_get_settings_returns_settings_instance():
    """get_settings() should return a Settings object."""
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_settings_has_expected_attributes():
    """Settings should have all expected configuration attributes."""
    settings = get_settings()
    for attr in (
        "bot_token",
        "fireworks_api_key",
        "gemini_api_keys",
        "tavily_api_key",
        "firecrawl_api_key",
        "serpapi_key",
        "default_model",
    ):
        assert hasattr(settings, attr)


def test_default_model_defaults_to_gemini_flash():
    """default_model should fall back to gemini-flash."""
    settings = Settings()
    assert settings.default_model == "gemini-flash"


def test_gemini_api_keys_is_a_list():
    """gemini_api_keys should always be a list."""
    settings = get_settings()
    assert isinstance(settings.gemini_api_keys, list)


def test_parse_csv_splits_and_strips():
    """_parse_csv should split on commas and strip whitespace."""
    assert _parse_csv("a, b ,c") == ["a", "b", "c"]


def test_parse_csv_handles_empty():
    """_parse_csv should return an empty list for empty or None input."""
    assert _parse_csv("") == []
    assert _parse_csv(None) == []
    assert _parse_csv(" , , ") == []


def test_validate_settings_raises_when_required_missing():
    """validate_settings should raise if required keys are absent."""
    with pytest.raises(RuntimeError) as exc:
        validate_settings(Settings())
    assert "BOT_TOKEN" in str(exc.value)


def test_validate_settings_passes_with_required_present():
    """validate_settings should pass when required keys are present."""
    settings = Settings(
        bot_token="token",
        fireworks_api_key="fw",
        gemini_api_keys=["k1"],
    )
    validate_settings(settings)  # should not raise
