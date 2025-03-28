import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Optional

class ConfigManager:
    """Centralized configuration manager for the application."""
    
    def __init__(self):
        # Load environment variables
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)
        
        # Initialize user preferences
        self.prefs_dir = Path.home() / ".personachat"
        self.prefs_file = self.prefs_dir / "prefs.json"
        os.makedirs(self.prefs_dir, exist_ok=True)
        
        try:
            with open(self.prefs_file, "r") as f:
                self.user_prefs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.user_prefs = {"api_keys": {}, "settings": {}}

    def get_env_variable(self, key: str) -> Optional[str]:
        """Get a value from environment variables."""
        return os.getenv(key)

    def get_api_key(self, service_name: str) -> Optional[str]:
        """Get an API key, checking user prefs first then environment."""
        # Check user preferences first
        if "api_keys" in self.user_prefs and service_name in self.user_prefs["api_keys"]:
            return self.user_prefs["api_keys"][service_name]
        
        # Fall back to environment variable
        env_key = f"{service_name.upper()}_API_KEY"
        return self.get_env_variable(env_key)

    def get_credential(self, service: str, cred_name: str) -> Optional[str]:
        """Get a credential, checking user prefs first then environment."""
        # Check user preferences first
        if "credentials" in self.user_prefs and service in self.user_prefs["credentials"]:
            return self.user_prefs["credentials"][service].get(cred_name)
        
        # Fall back to environment variable
        env_key = f"{service.upper()}_{cred_name.upper()}"
        return self.get_env_variable(env_key)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting from user prefs or environment."""
        if "settings" in self.user_prefs and key in self.user_prefs["settings"]:
            return self.user_prefs["settings"][key]
        return self.get_env_variable(key) or default

    def set_setting(self, key: str, value: Any) -> None:
        """Update a setting in user preferences."""
        if "settings" not in self.user_prefs:
            self.user_prefs["settings"] = {}
        self.user_prefs["settings"][key] = value
        self.save_user_prefs()

    def save_user_prefs(self) -> None:
        """Save user preferences to JSON file."""
        with open(self.prefs_file, "w") as f:
            json.dump(self.user_prefs, f, indent=2)

    def set_api_key(self, service_name: str, key: str) -> None:
        """Update an API key in user preferences."""
        if "api_keys" not in self.user_prefs:
            self.user_prefs["api_keys"] = {}
        self.user_prefs["api_keys"][service_name] = key
        self.save_user_prefs()