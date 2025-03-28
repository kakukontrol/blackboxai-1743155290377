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

class GoogleProvider(AIProvider):
    """AI provider for Google's Gemini models."""
    
    def __init__(self, config_manager: ConfigManager):
        self.api_key = config_manager.get_setting("GOOGLE_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        if not self.api_key:
            logging.warning("Google API key not configured - provider disabled")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        if not self.api_key:
            raise ValueError("Google API key not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/models/{model}:generateContent?key={self.api_key}",
                    json={
                        "contents": [
                            {
                                "parts": [{"text": msg["content"]}],
                                "role": msg["role"].upper()
                            } 
                            for msg in messages
                        ],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": max_tokens
                        }
                    },
                    timeout=30
                )
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except httpx.HTTPStatusError as e:
            logging.error(f"Google API error: {e.response.text}")
            raise ValueError(f"Google API error: {e.response.status_code}")
        except Exception as e:
            logging.error(f"Google request failed: {str(e)}")
            raise ValueError(f"Google request failed: {str(e)}")

    async def list_models(self) -> List[str]:
        return [
            "gemini-pro",
            "gemini-1.5-pro",
            "gemini-ultra"
        ]

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

class TogetherProvider(AIProvider):
    """AI provider for Together AI's models."""
    
    def __init__(self, config_manager: ConfigManager):
        self.api_key = config_manager.get_setting("TOGETHER_API_KEY")
        self.base_url = "https://api.together.xyz/v1"
        if not self.api_key:
            logging.warning("Together API key not configured - provider disabled")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        if not self.api_key:
            raise ValueError("Together API key not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=30
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logging.error(f"Together API error: {e.response.text}")
            raise ValueError(f"Together API error: {e.response.status_code}")
        except Exception as e:
            logging.error(f"Together request failed: {str(e)}")
            raise ValueError(f"Together request failed: {str(e)}")

    async def list_models(self) -> List[str]:
        return [
            "togethercomputer/llama-2-70b-chat",
            "togethercomputer/llama-3-70b",
            "mistralai/Mixtral-8x7B-Instruct-v0.1"
        ]

class AIServiceManager:
    """Manages multiple AI providers."""
    
    def __init__(self, config_manager: ConfigManager):
        self.providers = {}
        
        # Initialize all providers
        try:
            self.providers["groq"] = GroqProvider(config_manager)
        except Exception as e:
            logging.warning(f"Failed to initialize Groq provider: {str(e)}")
            
        try:
            self.providers["openrouter"] = OpenRouterProvider(config_manager)
        except Exception as e:
            logging.warning(f"Failed to initialize OpenRouter provider: {str(e)}")
            
        try:
            self.providers["google"] = GoogleProvider(config_manager)
        except Exception as e:
            logging.warning(f"Failed to initialize Google provider: {str(e)}")
            
        try:
            self.providers["together"] = TogetherProvider(config_manager)
        except Exception as e:
            logging.warning(f"Failed to initialize Together provider: {str(e)}")

        # Log available providers
        logging.info(f"Initialized AI providers: {list(self.providers.keys())}")