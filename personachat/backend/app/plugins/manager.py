import importlib
import inspect
import os
from pathlib import Path
from typing import List, Dict, Type, Optional, Any
from fastapi import FastAPI
from fastapi.routing import APIRouter
from .base import BasePlugin, PluginContext
from app.core.config import ConfigManager

class PluginManager:
    """Manages plugin discovery, loading, and execution."""
    
    def __init__(self, app: FastAPI, context: PluginContext):
        self.app = app
        self.context = context
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_settings: Dict[str, Dict[str, Any]] = {}
        self.plugin_states: Dict[str, bool] = {}
        
        # Set plugins directory path
        self.plugins_dir = Path(__file__).parent.parent.parent / "plugins_available"
        
        # Load initial settings/states from config
        self._load_initial_settings()
        
        # Discover and load plugins
        self.discover_and_load_plugins()

    def _load_initial_settings(self):
        """Load initial plugin settings from config manager."""
        user_prefs = self.context.config_manager.user_prefs
        if "plugins" in user_prefs:
            self.plugin_settings = user_prefs["plugins"].get("settings", {})
            self.plugin_states = user_prefs["plugins"].get("states", {})

    def _save_plugin_settings(self):
        """Save current plugin settings to config."""
        self.context.config_manager.set_setting(
            "plugins",
            {
                "settings": self.plugin_settings,
                "states": self.plugin_states
            }
        )
        self.context.config_manager.save_user_prefs()

    def discover_and_load_plugins(self):
        """Discover and load all available plugins."""
        if not self.plugins_dir.exists():
            return
            
        for entry in os.listdir(self.plugins_dir):
            path = self.plugins_dir / entry
            
            # Skip non-Python files and __pycache__
            if not (path.is_dir() or entry.endswith('.py')) or entry.startswith('_'):
                continue
                
            module_name = entry[:-3] if entry.endswith('.py') else entry
            plugin_id = f"plugins_available.{module_name}"
            
            try:
                module = importlib.import_module(plugin_id)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BasePlugin) and 
                        obj != BasePlugin):
                        try:
                            plugin = obj()
                            plugin.initialize(self.context)
                            
                            # Set initial state
                            plugin._enabled = self.plugin_states.get(plugin_id, True)
                            
                            # Load settings if available
                            if plugin_id in self.plugin_settings:
                                plugin.update_settings(self.plugin_settings[plugin_id])
                            
                            self.plugins[plugin_id] = plugin
                            
                            # Register API routes
                            router = plugin.register_api_routes()
                            if router:
                                self.app.include_router(
                                    router,
                                    prefix=f"/plugins/{module_name}"
                                )
                                
                        except Exception as e:
                            print(f"Error initializing plugin {plugin_id}: {e}")
                            
            except ImportError as e:
                print(f"Error importing plugin {plugin_id}: {e}")

    def get_plugin_list(self) -> List[Dict[str, Any]]:
        """Get list of all loaded plugins with their info."""
        return [
            {
                "id": plugin_id,
                "name": plugin.get_name(),
                "description": plugin.get_description(),
                "enabled": plugin.is_enabled,
                "settings_schema": plugin.get_settings_schema()
            }
            for plugin_id, plugin in self.plugins.items()
        ]

    def enable_plugin(self, plugin_id: str):
        """Enable a plugin by ID."""
        if plugin_id in self.plugins:
            self.plugins[plugin_id]._enabled = True
            self.plugin_states[plugin_id] = True
            self._save_plugin_settings()

    def disable_plugin(self, plugin_id: str):
        """Disable a plugin by ID."""
        if plugin_id in self.plugins:
            self.plugins[plugin_id]._enabled = False
            self.plugin_states[plugin_id] = False
            self._save_plugin_settings()

    def update_plugin_settings(self, plugin_id: str, settings: Dict[str, Any]):
        """Update settings for a plugin."""
        if plugin_id in self.plugins:
            self.plugins[plugin_id].update_settings(settings)
            self.plugin_settings[plugin_id] = settings
            self._save_plugin_settings()

    async def run_process_input_hooks(self, text: str, context: Dict[str, Any]) -> str:
        """Run all enabled plugins' input processing hooks."""
        for plugin in self.plugins.values():
            if plugin.is_enabled:
                try:
                    result = await plugin.process_input(text, context)
                    if result is not None:
                        text = result
                        if context.get('bypass_ai', False):
                            return text  # Skip further processing if bypass_ai is set
                        if text == "":  # Stop processing if empty string returned
                            break
                except Exception as e:
                    print(f"Error in plugin {plugin.get_name()} input processing: {e}")
        return text

    async def run_process_output_hooks(self, text: str, context: Dict[str, Any]) -> str:
        """Run all enabled plugins' output processing hooks."""
        for plugin in self.plugins.values():
            if plugin.is_enabled:
                try:
                    result = await plugin.process_output(text, context)
                    if result is not None:
                        text = result
                except Exception as e:
                    print(f"Error in plugin {plugin.get_name()} output processing: {e}")
        return text