"""Tests for GeminiProvider key rotation logic."""

import time
from unittest.mock import patch

from bot.providers.gemini import (
    GeminiProvider,
    KeyState,
    KeyStatus,
    RATE_LIMIT_COOLDOWN,
)


def _make_provider(num_keys: int = 3) -> GeminiProvider:
    """Create a GeminiProvider with mock keys."""
    fake_keys = [f"fake-key-{i}" for i in range(num_keys)]
    with patch("bot.providers.gemini.get_settings") as mock_settings:
        mock_settings.return_value.gemini_api_keys = fake_keys
        provider = GeminiProvider()
    return provider


def test_provider_initializes_with_all_keys():
    """GeminiProvider should initialize with all configured keys."""
    provider = _make_provider(num_keys=4)
    assert len(provider._keys) == 4
    for key_state in provider._keys:
        assert isinstance(key_state, KeyState)
        assert key_state.status == KeyStatus.HEALTHY


def test_get_next_key_returns_a_key():
    """_get_next_key should return a healthy key."""
    provider = _make_provider(num_keys=3)
    key_state = provider._get_next_key()
    assert key_state is not None
    assert key_state.status == KeyStatus.HEALTHY
    assert key_state.key.startswith("fake-key-")


def test_get_next_key_round_robin():
    """_get_next_key should cycle through keys in round-robin order."""
    provider = _make_provider(num_keys=3)
    keys_selected = []
    for _ in range(6):
        key_state = provider._get_next_key()
        keys_selected.append(key_state.key)

    # Should cycle: 0, 1, 2, 0, 1, 2
    assert keys_selected == [
        "fake-key-0", "fake-key-1", "fake-key-2",
        "fake-key-0", "fake-key-1", "fake-key-2",
    ]


def test_mark_rate_limited_removes_from_rotation():
    """A rate-limited key should be skipped during rotation."""
    provider = _make_provider(num_keys=3)

    # Get first key (index 0) and mark it rate limited
    key_state = provider._get_next_key()
    assert key_state.key == "fake-key-0"
    provider._mark_rate_limited(key_state)

    # Next selections should skip key 0
    next_key = provider._get_next_key()
    assert next_key.key == "fake-key-1"

    next_key = provider._get_next_key()
    assert next_key.key == "fake-key-2"

    # Should still skip key 0 (still in cooldown)
    next_key = provider._get_next_key()
    assert next_key.key == "fake-key-1"


def test_all_keys_rate_limited_returns_none():
    """If all keys are rate limited and in cooldown, returns None."""
    provider = _make_provider(num_keys=2)

    # Mark all keys as rate limited with future cooldown
    for key_state in provider._keys:
        key_state.status = KeyStatus.RATE_LIMITED
        key_state.cooldown_until = time.time() + 9999

    result = provider._get_next_key()
    assert result is None


def test_key_recovery_after_cooldown():
    """A rate-limited key should recover after the cooldown period expires."""
    provider = _make_provider(num_keys=2)

    # Mark first key as rate limited but with expired cooldown
    provider._keys[0].status = KeyStatus.RATE_LIMITED
    provider._keys[0].cooldown_until = time.time() - 1  # Cooldown already expired

    # The key should be available again
    key_state = provider._get_next_key()
    assert key_state is not None
    assert key_state.key == "fake-key-0"
    assert key_state.status == KeyStatus.HEALTHY


def test_mark_rate_limited_sets_cooldown():
    """_mark_rate_limited should set the cooldown_until timestamp."""
    provider = _make_provider(num_keys=1)
    key_state = provider._keys[0]

    before = time.time()
    provider._mark_rate_limited(key_state)
    after = time.time()

    assert key_state.status == KeyStatus.RATE_LIMITED
    assert key_state.cooldown_until >= before + RATE_LIMIT_COOLDOWN
    assert key_state.cooldown_until <= after + RATE_LIMIT_COOLDOWN


def test_mark_error_sets_status():
    """_mark_error should set the key status to ERROR."""
    provider = _make_provider(num_keys=1)
    key_state = provider._keys[0]

    provider._mark_error(key_state)
    assert key_state.status == KeyStatus.ERROR
