import httpx
from typing import Optional, Dict, Any
from app.core.config import ConfigManager

class TavilyClient:
    """Client for interacting with the Tavily search API."""
    
    BASE_URL = "https://api.tavily.com"
    
    def __init__(self, config_manager: ConfigManager):
        self.api_key = config_manager.get_setting("TAVILY_API_KEY")
        
    async def search(
        self, 
        query: str, 
        max_results: int = 5, 
        include_answer: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Perform a web search using Tavily API."""
        if not self.api_key:
            raise ValueError("Tavily API key not configured")
            
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": include_answer
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/search",
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            print(f"Request to Tavily API failed: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"Tavily API returned error: {e.response.status_code}")
            return None