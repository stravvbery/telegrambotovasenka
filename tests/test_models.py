"""Tests for bot.models module."""

from bot.models import AVAILABLE_MODELS, ModelInfo


def test_available_models_has_five_entries():
    """AVAILABLE_MODELS should have exactly 5 models."""
    assert len(AVAILABLE_MODELS) == 5


def test_all_expected_model_ids_present():
    """All expected model IDs should be in AVAILABLE_MODELS."""
    expected_ids = ["deepseek-v4", "kimi-k2.6", "glm-5.1", "qwen-3.6-plus", "gemini-flash"]
    actual_ids = [m.id for m in AVAILABLE_MODELS]
    for expected in expected_ids:
        assert expected in actual_ids, f"Model '{expected}' not found in AVAILABLE_MODELS"


def test_model_info_has_required_fields():
    """Each ModelInfo object should have id, name, provider, and supports_tools fields."""
    for model in AVAILABLE_MODELS:
        assert isinstance(model, ModelInfo)
        assert model.id
        assert model.name
        assert model.provider
        assert isinstance(model.supports_tools, bool)


def test_model_info_has_model_id():
    """Each ModelInfo should have a model_id for the actual API model identifier."""
    for model in AVAILABLE_MODELS:
        assert model.model_id
        assert isinstance(model.model_id, str)


def test_deepseek_model_is_fireworks_provider():
    """DeepSeek model should use the fireworks provider."""
    deepseek = next(m for m in AVAILABLE_MODELS if m.id == "deepseek-v4")
    assert deepseek.provider == "fireworks"
    assert deepseek.name == "DeepSeek V4"


def test_gemini_flash_is_google_provider():
    """Gemini Flash model should use the google provider."""
    gemini = next(m for m in AVAILABLE_MODELS if m.id == "gemini-flash")
    assert gemini.provider == "google"
    assert gemini.name == "Gemini Flash"


def test_all_models_support_tools():
    """All current models should support tools."""
    for model in AVAILABLE_MODELS:
        assert model.supports_tools is True
