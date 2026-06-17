from typing import Protocol

from app.core.exceptions import ConfigError
from config.settings import get_settings


class AIProvider(Protocol):
    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str: ...

    async def embed(self, text: str) -> list[float]: ...

    @property
    def model_name(self) -> str: ...


def get_ai_provider(provider_name: str = "gemini") -> AIProvider:
    if provider_name != "gemini":
        raise ConfigError(f"Unsupported AI provider: {provider_name}")

    from app.ai.gemini_provider import GeminiProvider

    settings = get_settings()
    if settings.gemini_api_key is None:
        raise ConfigError("GEMINI_API_KEY is required for the Gemini provider")
    return GeminiProvider(
        api_key=settings.gemini_api_key.get_secret_value(),
        model_name=settings.gemini_model,
    )
