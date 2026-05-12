from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    role: str
    content: str


@dataclass
class ChatRequest:
    messages: list[Message]
    model: str = "gemini-flash"
    use_search: bool = False


@dataclass
class ChatResponse:
    content: str
    model_used: str
    search_used: bool = False


@dataclass
class ModelInfo:
    id: str
    name: str
    provider: str
    model_id: str
    supports_tools: bool = False


AVAILABLE_MODELS: list[ModelInfo] = [
    ModelInfo(
        id="deepseek-v4",
        name="DeepSeek V4",
        provider="fireworks",
        model_id="accounts/fireworks/models/deepseek-v3",
        supports_tools=True,
    ),
    ModelInfo(
        id="kimi-k2.6",
        name="Kimi K2.6",
        provider="fireworks",
        model_id="accounts/fireworks/models/kimi-k2",
        supports_tools=True,
    ),
    ModelInfo(
        id="glm-5.1",
        name="GLM 5.1",
        provider="fireworks",
        model_id="accounts/fireworks/models/glm-4",
        supports_tools=True,
    ),
    ModelInfo(
        id="qwen-3.6-plus",
        name="Qwen 3.6 Plus",
        provider="fireworks",
        model_id="accounts/fireworks/models/qwen2p5-72b-instruct",
        supports_tools=True,
    ),
    ModelInfo(
        id="gemini-flash",
        name="Gemini Flash",
        provider="google",
        model_id="gemini-2.0-flash",
        supports_tools=True,
    ),
]
