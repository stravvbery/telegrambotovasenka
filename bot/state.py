from bot.config import get_settings
from bot.models import Message

MAX_HISTORY = 10


class UserState:
    """Simple in-memory user state storage."""

    def __init__(self) -> None:
        self._user_models: dict[int, str] = {}
        self._user_history: dict[int, list[Message]] = {}

    def get_user_model(self, user_id: int) -> str:
        """Return the selected model for a user, or the default model."""
        return self._user_models.get(user_id, get_settings().default_model)

    def set_user_model(self, user_id: int, model: str) -> None:
        """Set the selected model for a user."""
        self._user_models[user_id] = model

    def get_history(self, user_id: int) -> list[Message]:
        """Return conversation history for a user."""
        return self._user_history.get(user_id, [])

    def add_to_history(self, user_id: int, role: str, content: str) -> None:
        """Add a message to user history, keeping at most MAX_HISTORY entries."""
        if user_id not in self._user_history:
            self._user_history[user_id] = []
        self._user_history[user_id].append(Message(role=role, content=content))
        if len(self._user_history[user_id]) > MAX_HISTORY:
            self._user_history[user_id] = self._user_history[user_id][-MAX_HISTORY:]

    def clear_history(self, user_id: int) -> None:
        """Clear conversation history for a user."""
        self._user_history.pop(user_id, None)


# Module-level instance for shared access
_state = UserState()


def get_user_model(user_id: int) -> str:
    return _state.get_user_model(user_id)


def set_user_model(user_id: int, model: str) -> None:
    _state.set_user_model(user_id, model)


def get_history(user_id: int) -> list[Message]:
    return _state.get_history(user_id)


def add_to_history(user_id: int, role: str, content: str) -> None:
    _state.add_to_history(user_id, role, content)


def clear_history(user_id: int) -> None:
    _state.clear_history(user_id)
