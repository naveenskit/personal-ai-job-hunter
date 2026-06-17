import asyncio

import google.generativeai as genai

from app.core.exceptions import ExternalServiceError
from app.core.retry import async_retry


class GeminiProvider:
    def __init__(self, *, api_key: str, model_name: str = "gemini-1.5-flash") -> None:
        self._model_name = model_name
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)

    @property
    def model_name(self) -> str:
        return self._model_name

    @async_retry(attempts=3, base_delay=0.75, retry_on=(ExternalServiceError,))
    async def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        full_prompt = f"{system.strip()}\n\n{prompt.strip()}" if system else prompt

        def _call() -> str:
            response = self._model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            text = getattr(response, "text", None)
            if not text:
                raise ExternalServiceError("Gemini returned an empty response")
            return text

        try:
            return await asyncio.to_thread(_call)
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError(
                "Gemini completion failed",
                details={"error": str(exc)},
            ) from exc

    @async_retry(attempts=3, base_delay=0.75, retry_on=(ExternalServiceError,))
    async def embed(self, text: str) -> list[float]:
        def _call() -> list[float]:
            response = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
            )
            embedding = response.get("embedding")
            if not isinstance(embedding, list):
                raise ExternalServiceError("Gemini returned an invalid embedding")
            return [float(value) for value in embedding]

        try:
            return await asyncio.to_thread(_call)
        except ExternalServiceError:
            raise
        except Exception as exc:
            raise ExternalServiceError(
                "Gemini embedding failed",
                details={"error": str(exc)},
            ) from exc
