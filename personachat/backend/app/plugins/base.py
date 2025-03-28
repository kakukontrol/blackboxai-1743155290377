from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable, List
from fastapi.routing import APIRouter
from app.core.config import ConfigManager
from app.storage.vector_store import VectorStoreInterface
from app.core.embeddings import EmbeddingGenerator
from app.services.ai_service import AIServiceManager
from app.storage.chat_history import ChatHistoryManager

class PluginContext:
    """Context object providing access to core application managers."""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        ai_service_manager: AIServiceManager,
        chat_history_manager: ChatHistoryManager,
        vector_store: VectorStoreInterface,
        embedding_generator: EmbeddingGenerator
    ):
        self.config_manager = config_manager
        self.ai_service_manager = ai_service_manager
        self.chat_history_manager = chat_history_manager
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator

class BasePlugin(ABC):
    """Abstract base class that all plugins must implement."""
    
    def __init__(self):
        self._enabled = True
        self._context: Optional[PluginContext] = None

    @property
    def is_enabled(self) -> bool:
        """Whether the plugin is currently enabled."""
        return self._enabled

    @abstractmethod
    def get_name(self) -> str:
        """Returns the user-facing name of the plugin."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Returns a brief description of the plugin's functionality."""
        pass

    def initialize(self, context: PluginContext) -> None:
        """
        Called when the plugin is loaded. Provides access to core managers.
        Base implementation just stores the context.
        """
        self._context = context

    def register_api_routes(self) -> Optional[APIRouter]:
        """
        Allows the plugin to register custom API endpoints.
        Return None if no routes are needed.
        """
        return None

    async def process_input(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Process user input before it's sent to the AI.
        Return:
        - Modified text to use instead of original
        - None to indicate no changes
        - Set context['bypass_ai'] = True to skip AI processing
          and use returned text as final response
        """
        return None

    async def process_output(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Process AI output before it's sent to the user.
        Return modified text or None for no change.
        """
        return None

    def get_settings_schema(self) -> Optional[Dict[str, Any]]:
        """
        Define the settings schema for this plugin.
        Return None if no settings are needed.
        """
        return None

    def update_settings(self, settings: Dict[str, Any]) -> None:
        """
        Called when plugin settings are updated.
        Base implementation does nothing.
        """
        pass