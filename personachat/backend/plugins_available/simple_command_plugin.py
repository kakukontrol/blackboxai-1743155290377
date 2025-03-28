from typing import Optional, Dict, Any
from app.plugins.base import BasePlugin

class SimpleCommandPlugin(BasePlugin):
    """Example plugin that responds to /hello command."""
    
    def get_name(self) -> str:
        return "Simple Command Example"
    
    def get_description(self) -> str:
        return "Responds to the /hello command."
    
    def initialize(self, context) -> None:
        print(f"Initialized {self.get_name()} plugin")
    
    async def process_input(
        self, 
        text: str, 
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Handle /hello command and bypass AI processing."""
        if text.strip().lower() == "/hello":
            context['bypass_ai'] = True
            return "Plugin Response: Hello there!"
        return None