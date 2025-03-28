import os
import json
import logging
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Optional

class ConfigManager:
    """Centralized configuration manager for the application."""
    
    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "api_keys": {"type": "object"},
            "settings": {"type": "object"},
            "credentials": {"type": "object"},
            "config_version": {"type": "string", "default": "1.0"}
        },
        "additionalProperties": False
    }

    ENVIRONMENTS = {
        "development": {
            "api_keys": {},
            "settings": {
                "debug": True,
                "rate_limits": {
                    "api": {"requests": 100, "period": 60},
                    "ai": {"requests": 30, "period": 60}
                },
                "model_defaults": {
                    "groq": "llama3-8b-8192",
                    "openai": "gpt-3.5-turbo"
                }
            },
            "credentials": {},
            "config_version": "1.0"
        },
        "production": {
            "api_keys": {},
            "settings": {
                "debug": False,
                "rate_limits": {
                    "api": {"requests": 50, "period": 60},
                    "ai": {"requests": 15, "period": 60}
                },
                "model_defaults": {
                    "groq": "llama3-70b-8192",
                    "openai": "gpt-4"
                }
            },
            "credentials": {},
            "config_version": "1.0"
        }
    }

    def __init__(self):
        # Initialize encryption
        self.encryption_salt = os.getenv("ENCRYPTION_SALT", "default-salt-value").encode()
        self.encryption_key = self._get_encryption_key()
        
        # Determine the current environment
        self.environment = os.getenv("APP_ENV", "development")
        if self.environment not in self.ENVIRONMENTS:
            raise ValueError(f"Invalid environment: {self.environment}")

        # Load environment variables
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(dotenv_path=env_path)

        # Initialize user preferences
        self.prefs_dir = Path.home() / ".personachat"
        self.prefs_file = self.prefs_dir / "prefs.json"
        os.makedirs(self.prefs_dir, exist_ok=True)

        # Initialize with environment-specific config
        default_config = self.ENVIRONMENTS[self.environment]
        
        try:
            with open(self.prefs_file, "r") as f:
                loaded_config = json.load(f)
                self.user_prefs = self._validate_and_migrate(loaded_config, default_config)
        except (FileNotFoundError, json.JSONDecodeError):
            self.user_prefs = default_config

    def _get_encryption_key(self) -> bytes:
        """Generate a key for encryption based on a password and salt."""
        password = os.getenv("ENCRYPTION_PASSWORD", "default-password").encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.encryption_salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        fernet = Fernet(self.encryption_key)
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        fernet = Fernet(self.encryption_key)
        decrypted_data = fernet.decrypt(encrypted_data.encode())
        return decrypted_data.decode()

    def get_rate_limit(self, endpoint: str) -> dict:
        """Get rate limit settings for a specific endpoint."""
        return self.get_setting(f"rate_limits.{endpoint}", {"requests": 60, "period": 60})

    def get_model_default(self, provider: str) -> str:
        """Get default model for a provider."""
        return self.get_setting(f"model_defaults.{provider}", "")

    def _validate_and_migrate(self, config: dict, default_config: dict) -> dict:
        """Validate config structure and migrate if needed."""
        # Basic validation
        if not isinstance(config, dict):
            return default_config
            
        # Version migration
        if "config_version" not in config:
            config = self._migrate_v0_to_v1(config)
            
        # Schema validation
        try:
            import jsonschema
            jsonschema.validate(instance=config, schema=self.CONFIG_SCHEMA)
            return config
        except ImportError:
            logging.warning("jsonschema not available, skipping config validation")
            return config
        except Exception as e:
            logging.error(f"Invalid config: {str(e)}. Using defaults.")
            return default_config

    def _migrate_v0_to_v1(self, old_config: dict) -> dict:
        """Migrate from version 0 (no version) to version 1."""
        migrated = {
            "api_keys": old_config.get("api_keys", {}),
            "settings": old_config.get("settings", {}),
            "credentials": old_config.get("credentials", {}),
            "config_version": "1.0"
        }
        return migrated

    def get_env_variable(self, key: str) -> Optional[str]:
        """Get a value from environment variables."""
        return os.getenv(key)

    def get_api_key(self, service_name: str) -> Optional[str]:
        """Get an API key, checking user prefs first then environment."""
        if "api_keys" in self.user_prefs and service_name in self.user_prefs["api_keys"]:
            return self.user_prefs["api_keys"][service_name]
        
        env_key = f"{service_name.upper()}_API_KEY"
        return self.get_env_variable(env_key)

    def get_credential(self, service: str, cred_name: str) -> Optional[str]:
        """Get a credential, checking user prefs first then environment."""
        if "credentials" in self.user_prefs and service in self.user_prefs["credentials"]:
            return self.user_prefs["credentials"][service].get(cred_name)
        
        env_key = f"{service.upper()}_{cred_name.upper()}"
        return self.get_env_variable(env_key)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting from user prefs or environment."""
        # Check nested settings (e.g. rate_limits.api)
        if "." in key:
            section, subkey = key.split(".", 1)
            if "settings" in self.user_prefs and section in self.user_prefs["settings"]:
                if isinstance(self.user_prefs["settings"][section], dict):
                    return self.user_prefs["settings"][section].get(subkey, default)
        
        # Check regular settings
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