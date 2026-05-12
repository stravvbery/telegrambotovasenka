"""Tests for bot.config module."""

from bot.config import Settings, get_settings


def test_get_settings_returns_settings_instance():
    """get_settings() should return a Settings object."""
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_settings_has_bot_token():
    """Settings should have a bot_token loaded from .env."""
    settings = get_settings()
    assert settings.bot_token
    assert isinstance(settings.bot_token, str)
    assert len(settings.bot_token) > 0


def test_settings_gemini_api_keys_is_list_of_six():
    """Settings should have gemini_api_keys as a list of 6 keys."""
    settings = get_settings()
    assert isinstance(settings.gemini_api_keys, list)
    assert len(settings.gemini_api_keys) == 6
    for key in settings.gemini_api_keys:
        assert isinstance(key, str)
        assert len(key) > 0


def test_settings_default_model_has_value():
    """Settings should have a default_model with a value."""
    settings = get_settings()
    assert settings.default_model
    assert isinstance(settings.default_model, str)
    assert settings.default_model == "gemini-flash"


def test_settings_has_expected_attributes():
    """Settings should have all expected configuration attributes."""
    settings = get_settings()
    assert hasattr(settings, "bot_token")
    assert hasattr(settings, "fireworks_api_key")
    assert hasattr(settings, "gemini_api_keys")
    assert hasattr(settings, "tavily_api_key")
    assert hasattr(settings, "firecrawl_api_key")
    assert hasattr(settings, "serpapi_key")
    assert hasattr(settings, "default_model")
