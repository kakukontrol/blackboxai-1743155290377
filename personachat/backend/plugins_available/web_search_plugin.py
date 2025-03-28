from typing import Optional, Dict, Any
from app.plugins.base import BasePlugin
from app.integrations.tavily_client import TavilyClient

class WebSearchPlugin(BasePlugin):
    """Plugin that adds web search capability using Tavily API."""
    
    def __init__(self):
        super().__init__()
        self.tavily_client = None
        
    def get_name(self) -> str:
        return "Web Search (Tavily)"
        
    def get_description(self) -> str:
        return "Adds web search capability using Tavily API via /search command."
        
    def initialize(self, context):
        self.tavily_client = TavilyClient(context.config_manager)
        
    async def process_input(self, text: str, context: Dict[str, Any]) -> Optional[str]:
        """Process /search commands."""
        if not text.strip().lower().startswith("/search "):
            return None
            
        query = text.strip()[len("/search "):]
        if not query:
            context['bypass_ai'] = True
            return "Usage: /search <your query>"
            
        try:
            results = await self.tavily_client.search(query)
            if not results:
                context['bypass_ai'] = True
                return "Web search failed."
                
            # Format results
            formatted = []
            if results.get('answer'):
                formatted.append(f"Answer: {results['answer']}\n")
                
            formatted.append("Search Results:")
            for i, result in enumerate(results.get('results', [])[:5], 1):
                formatted.append(
                    f"{i}. {result.get('title', 'No title')}\n"
                    f"   {result.get('url', 'No URL')}\n"
                    f"   {result.get('content', 'No content')}"
                )
                
            context['bypass_ai'] = True
            return "\n\n".join(formatted)
            
        except Exception as e:
            print(f"Web search error: {e}")
            context['bypass_ai'] = True
            return "Web search failed due to an error."