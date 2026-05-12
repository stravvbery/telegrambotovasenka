from bot.models import AVAILABLE_MODELS, ModelInfo
from bot.providers import BaseLLMProvider
from bot.providers.fireworks import FireworksProvider
from bot.providers.gemini import GeminiProvider


class ProviderRouter:
    """Routes model requests to the appropriate provider."""

    def __init__(self) -> None:
        self._fireworks = FireworksProvider()
        self._gemini = GeminiProvider()
        self._model_map: dict[str, ModelInfo] = {
            m.id: m for m in AVAILABLE_MODELS
        }

    def get_provider(self, model_name: str) -> BaseLLMProvider:
        """Get the appropriate provider for a model name.

        Args:
            model_name: The model identifier (e.g., 'gemini-flash', 'deepseek-v4').

        Returns:
            The provider instance that handles this model.

        Raises:
            ValueError: If the model name is not recognized.
        """
        model_info = self._model_map.get(model_name)
        if model_info is None:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Available: {list(self._model_map.keys())}"
            )

        if model_info.provider == "fireworks":
            return self._fireworks
        elif model_info.provider == "google":
            return self._gemini
        else:
            raise ValueError(f"Unknown provider: {model_info.provider}")

    def get_model_id(self, model_name: str) -> str:
        """Get the actual model ID to send to the API.

        Args:
            model_name: The model identifier (e.g., 'gemini-flash').

        Returns:
            The API model ID string.
        """
        model_info = self._model_map.get(model_name)
        if model_info is None:
            raise ValueError(f"Unknown model: {model_name}")
        return model_info.model_id

    def list_models(self) -> list[ModelInfo]:
        """Return all available models."""
        return AVAILABLE_MODELS
