from pathlib import Path
from typing import Optional
import os
from huggingface_hub import (
    hf_hub_download,
    list_repo_files,
    login,
    constants,
    HfFileSystem
)
from huggingface_hub.utils import EntryNotFoundError
from app.core.config import ConfigManager
import logging

class HuggingFaceHubClient:
    """Client for interacting with Hugging Face Hub."""
    
    def __init__(self, config_manager: ConfigManager):
        self.token = config_manager.get_setting("HUGGINGFACE_HUB_TOKEN")
        self.authenticated = False
        
        if self.token:
            try:
                login(token=self.token)
                self.authenticated = True
                logging.info("Logged in to Hugging Face Hub")
            except Exception as e:
                logging.error(f"HF Hub login failed: {str(e)}")

    def download_model_file(
        self,
        repo_id: str,
        filename: str,
        cache_dir: Optional[str] = None
    ) -> Optional[str]:
        """Download a file from Hugging Face Hub."""
        try:
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                cache_dir=cache_dir or str(Path.home() / ".personachat" / "models"),
                token=self.token if self.authenticated else None
            )
            return local_path
        except EntryNotFoundError:
            logging.error(f"File not found in repo {repo_id}: {filename}")
        except Exception as e:
            logging.error(f"Failed to download from HF Hub: {str(e)}")
        return None

    def check_file_exists(self, repo_id: str, filename: str) -> bool:
        """Check if a file exists in a HF Hub repo."""
        try:
            files = list_repo_files(
                repo_id,
                token=self.token if self.authenticated else None
            )
            return filename in files
        except Exception as e:
            logging.error(f"Failed to list repo files: {str(e)}")
            return False

    def list_models(self, search_term: str) -> Optional[list]:
        """List available models matching search term."""
        try:
            fs = HfFileSystem(token=self.token)
            return [x for x in fs.glob(f"models/{search_term}*")]
        except Exception as e:
            logging.error(f"Failed to list models: {str(e)}")
            return None