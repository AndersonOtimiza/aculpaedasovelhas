"""
LLM integration service supporting Ollama, OpenAI, and Anthropic.
"""
import httpx
from typing import Dict, Any
from abc import ABC, abstractmethod
from src.config.settings import settings
from src.config.constants import EXEG_AI_SYSTEM_PROMPT


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = EXEG_AI_SYSTEM_PROMPT,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate response from LLM."""
        pass


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider."""

    def __init__(self):
        self.url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def generate(
        self,
        prompt: str,
        system_prompt: str = EXEG_AI_SYSTEM_PROMPT,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate using Ollama API."""
        full_prompt = f"[Sistema]: {system_prompt}\n\n[Usuario]: {prompt}\n\n[Assistente]:"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": 0.9,
                        "num_predict": 2048,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()

            return {
                "response": result.get("response", ""),
                "model": self.model,
                "provider": "ollama",
                "tokens_used": result.get("eval_count"),
            }


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str = EXEG_AI_SYSTEM_PROMPT,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate using OpenAI API."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            result = response.json()

            return {
                "response": result["choices"][0]["message"]["content"],
                "model": self.model,
                "provider": "openai",
                "tokens_used": result.get("usage", {}).get("total_tokens"),
            }


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM provider."""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str = EXEG_AI_SYSTEM_PROMPT,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate using Anthropic API."""
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 2048,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            result = response.json()

            return {
                "response": result["content"][0]["text"],
                "model": self.model,
                "provider": "anthropic",
                "tokens_used": result.get("usage", {}).get("input_tokens", 0)
                + result.get("usage", {}).get("output_tokens", 0),
            }


class LLMService:
    """Unified LLM service with multiple provider support."""

    def __init__(self):
        self.providers = {
            "ollama": OllamaProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
        }

    async def generate(
        self,
        prompt: str,
        provider: str = "ollama",
        system_prompt: str = EXEG_AI_SYSTEM_PROMPT,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate response using specified provider."""
        if provider not in self.providers:
            raise ValueError(
                f"Unknown provider: {provider}. Use: {list(self.providers.keys())}"
            )

        return await self.providers[provider].generate(prompt, system_prompt, temperature)

    async def check_health(self, provider: str = "ollama") -> Dict[str, Any]:
        """Check LLM provider health."""
        if provider == "ollama":
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.get(f"{settings.OLLAMA_URL}/api/tags")
                    if response.status_code == 200:
                        models = response.json().get("models", [])
                        return {
                            "status": "online",
                            "provider": "ollama",
                            "url": settings.OLLAMA_URL,
                            "models": [m.get("name") for m in models],
                        }
            except Exception as e:
                return {
                    "status": "offline",
                    "provider": "ollama",
                    "url": settings.OLLAMA_URL,
                    "error": str(e),
                }

        return {"status": "unknown", "provider": provider}


llm_service = LLMService()
