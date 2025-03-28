import abc
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import ConfigManager

class AIProvider(abc.ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    @abc.abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response from the AI provider."""
        pass

    async def list_models(self) -> List[str]:
        """List available models from this provider."""
        return []

class GroqProvider(AIProvider):
    """Implementation for Groq API."""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__(config_manager)
        self.api_key = config_manager.get_api_key("Groq")
        self.base_url = "https://api.groq.com/openai/v1"

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        if not self.api_key:
            raise ValueError("Groq API key not configured")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **({"max_tokens": max_tokens} if max_tokens else {})
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
        except httpx.RequestError as e:
            raise ValueError(f"Request error: {e}")
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API error: {e.response.text}")

    async def list_models(self) -> List[str]:
        return ["llama3-8b-8192", "mixtral-8x7b-32768"]

class OpenRouterProvider(AIProvider):
    """Implementation for OpenRouter API."""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__(config_manager)
        self.api_key = config_manager.get_api_key("OpenRouter")
        self.base_url = "https://openrouter.ai/api/v1"

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **({"max_tokens": max_tokens} if max_tokens else {})
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": "https://github.com/your-repo"
                    }
                )
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
        except httpx.RequestError as e:
            raise ValueError(f"Request error: {e}")
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API error: {e.response.text}")

    async def list_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                return [model["id"] for model in response.json()["data"]]
        except Exception:
            return ["gpt-3.5-turbo", "gpt-4", "claude-2"]

class AIServiceManager:
    """Manages multiple AI providers."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.providers: Dict[str, AIProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available providers based on config."""
        if self.config_manager.get_api_key("Groq"):
            self.providers["groq"] = GroqProvider(self.config_manager)
        if self.config_manager.get_api_key("OpenRouter"):
            self.providers["openrouter"] = OpenRouterProvider(self.config_manager)

    def get_available_providers(self) -> List[str]:
        """Get names of available providers."""
        return list(self.providers.keys())

    def get_provider(self, name: str) -> Optional[AIProvider]:
        """Get a provider instance by name."""
        return self.providers.get(name.lower())

    async def get_models_for_provider(self, name: str) -> List[str]:
        """Get available models for a provider."""
        provider = self.get_provider(name)
        if not provider:
            return []
        return await provider.list_models()

    async def call_ai(
        self,
        provider_name: str,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Call the specified AI provider."""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        try:
            return await provider.generate(messages, model, **kwargs)
        except Exception as e:
            raise ValueError(f"AI service error: {str(e)}")