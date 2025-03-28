import httpx
from typing import Optional, List, Dict

class ApiClient:
    """Client for communicating with the backend API."""
    
    BASE_URL = "http://127.0.0.1:8000"
    
    async def send_message(self, message: str, provider: str, model: str) -> str | None:
        """Send a message to the backend and return the response."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat",
                    json={
                        "message": message,
                        "provider": provider,
                        "model": model
                    }
                )
                response.raise_for_status()
                return response.json().get("response")
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
            return None

    def get_providers(self) -> List[str]:
        """Get available AI providers."""
        try:
            response = httpx.get(f"{self.BASE_URL}/providers")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting providers: {e}")
            return []

    def get_models(self, provider_name: str) -> List[str]:
        """Get available models for a provider."""
        try:
            response = httpx.get(f"{self.BASE_URL}/providers/{provider_name}/models")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting models: {e}")
            return []

    def get_settings(self) -> Dict:
        """Get current settings."""
        try:
            response = httpx.get(f"{self.BASE_URL}/settings")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting settings: {e}")
            return {}

    def save_settings(self, settings: Dict) -> bool:
        """Save settings to backend."""
        try:
            response = httpx.post(f"{self.BASE_URL}/settings", json=settings)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False