"""Tests for bot.state module."""

from bot.models import Message
from bot.state import UserState


def test_get_user_model_returns_default_when_not_set():
    """get_user_model should return the default model when user hasn't set one."""
    state = UserState()
    model = state.get_user_model(12345)
    assert model == "gemini-flash"


def test_set_and_get_user_model_roundtrip():
    """set_user_model followed by get_user_model should return the set model."""
    state = UserState()
    state.set_user_model(12345, "deepseek-v4")
    assert state.get_user_model(12345) == "deepseek-v4"


def test_set_user_model_different_users():
    """Different users should have independent model selections."""
    state = UserState()
    state.set_user_model(111, "deepseek-v4")
    state.set_user_model(222, "kimi-k2.6")
    assert state.get_user_model(111) == "deepseek-v4"
    assert state.get_user_model(222) == "kimi-k2.6"


def test_add_to_history_and_get_history():
    """add_to_history should add messages retrievable via get_history."""
    state = UserState()
    state.add_to_history(12345, "user", "Hello")
    state.add_to_history(12345, "assistant", "Hi there!")

    history = state.get_history(12345)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello"
    assert history[1].role == "assistant"
    assert history[1].content == "Hi there!"


def test_get_history_empty_for_new_user():
    """get_history should return empty list for a user with no history."""
    state = UserState()
    history = state.get_history(99999)
    assert history == []


def test_history_max_limit():
    """History should be limited to MAX_HISTORY (10) messages."""
    state = UserState()
    for i in range(15):
        state.add_to_history(12345, "user", f"Message {i}")

    history = state.get_history(12345)
    assert len(history) == 10
    # Should keep the most recent messages
    assert history[0].content == "Message 5"
    assert history[-1].content == "Message 14"


def test_clear_history():
    """clear_history should remove all history for a user."""
    state = UserState()
    state.add_to_history(12345, "user", "Hello")
    state.add_to_history(12345, "assistant", "Hi")

    state.clear_history(12345)
    history = state.get_history(12345)
    assert history == []


def test_clear_history_does_not_affect_other_users():
    """Clearing history for one user should not affect others."""
    state = UserState()
    state.add_to_history(111, "user", "Hello from 111")
    state.add_to_history(222, "user", "Hello from 222")

    state.clear_history(111)
    assert state.get_history(111) == []
    assert len(state.get_history(222)) == 1
