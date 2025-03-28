import os
from typing import Optional, Dict, Any
from clearml import Task, Logger
from app.core.config import ConfigManager
import logging

class ClearMLIntegration:
    """Client for ClearML experiment tracking and logging."""
    
    def __init__(self, config_manager: ConfigManager):
        self.task = None
        self.logger = None
        
        # Set environment variables before importing Task
        api_key = config_manager.get_setting("CLEARML_API_ACCESS_KEY")
        api_secret = config_manager.get_setting("CLEARML_API_SECRET_KEY")
        api_host = config_manager.get_setting("CLEARML_API_HOST")
        
        if api_key and api_secret:
            os.environ['CLEARML_API_ACCESS_KEY'] = api_key
            os.environ['CLEARML_API_SECRET_KEY'] = api_secret
            if api_host:
                os.environ['CLEARML_API_HOST'] = api_host
            
            try:
                self.task = Task.init(
                    project_name="PersonaChat",
                    task_name="Chat Sessions",
                    auto_connect_frameworks=False
                )
                if self.task:
                    self.logger = self.task.get_logger()
                    logging.info("ClearML integration initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize ClearML: {str(e)}")
        else:
            logging.warning("ClearML credentials not configured - tracking disabled")

    def log_chat_interaction(
        self,
        conversation_id: str,
        user_input: str,
        ai_response: str,
        provider: str,
        model: str,
        metadata: Optional[Dict] = None
    ):
        """Log a chat interaction to ClearML."""
        if not self.logger:
            return
            
        try:
            report_text = (
                f"Conversation ID: {conversation_id}\n"
                f"Provider: {provider}\n"
                f"Model: {model}\n"
                f"User Input: {user_input}\n"
                f"AI Response: {ai_response}"
            )
            self.logger.report_text(report_text, print_console=False)
            
            if metadata:
                self.logger.report_hyperparams({
                    'provider': provider,
                    'model': model,
                    'metadata': metadata
                })
        except Exception as e:
            logging.error(f"Failed to log to ClearML: {str(e)}")