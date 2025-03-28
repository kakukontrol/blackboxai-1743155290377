import uuid
import re
from typing import Optional, Dict, Any
from app.plugins.base import BasePlugin
from app.integrations.e2b_client import E2BClient
import logging

class CodeRunnerPlugin(BasePlugin):
    """Plugin that handles code execution in E2B sandboxes with command-based confirmation."""
    
    def __init__(self):
        super().__init__()
        self.e2b_client = None
        self.code_block_pattern = re.compile(r"```(\w+)?\n([\s\S]+?)\n```")
        self.pending_code: Dict[str, Dict] = {}  # request_id -> {'code': ..., 'language': ...}

    def get_name(self) -> str:
        return "Code Runner (E2B)"
        
    def get_description(self) -> str:
        return "Executes code blocks via /execute command after user confirmation"
        
    def initialize(self, context):
        self.e2b_client = E2BClient(context.config_manager)
        if not self.e2b_client.api_key:
            logging.warning("E2B client not usable due to missing API key")
        
    async def process_output(self, text: str, context: Dict[str, Any]) -> Optional[str]:
        """Process output to find code blocks and replace with execution instructions."""
        def replace_code_block(match):
            language = match.group(1) or "python"
            code = match.group(2)
            request_id = str(uuid.uuid4())
            self.pending_code[request_id] = {
                'code': code,
                'language': language
            }
            return f"[Code block detected (ID: {request_id}). Type /execute {request_id} to run or /deny {request_id} to cancel.]"
        
        if self.e2b_client and self.e2b_client.api_key:
            return self.code_block_pattern.sub(replace_code_block, text)
        return None
        
    async def process_input(self, text: str, context: Dict[str, Any]) -> Optional[str]:
        """Process /execute and /deny commands."""
        text = text.strip()
        if text.startswith("/execute "):
            request_id = text[len("/execute "):]
            if request_id in self.pending_code:
                code_data = self.pending_code.pop(request_id)
                try:
                    result = await self.e2b_client.run_code(
                        code_data['code'],
                        code_data['language']
                    )
                    output = []
                    if result.get('stdout'):
                        output.append(f"Output:\n{result['stdout']}")
                    if result.get('stderr'):
                        output.append(f"Errors:\n{result['stderr']}")
                    if result.get('error'):
                        output.append(f"Execution failed: {result['error']}")
                    context['bypass_ai'] = True
                    return "\n\n".join(output) if output else "Code executed (no output)"
                except Exception as e:
                    context['bypass_ai'] = True
                    return f"Code execution failed: {str(e)}"
            context['bypass_ai'] = True
            return "Invalid or expired execution ID."
            
        elif text.startswith("/deny "):
            request_id = text[len("/deny "):]
            if request_id in self.pending_code:
                self.pending_code.pop(request_id)
            context['bypass_ai'] = True
            return "Code execution cancelled."
            
        return None
