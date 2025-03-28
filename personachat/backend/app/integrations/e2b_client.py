import e2b
import asyncio
from typing import Dict, Optional, Any
from app.core.config import ConfigManager

class E2BClient:
    """Client for executing code in E2B sandboxes."""
    
    def __init__(self, config_manager: ConfigManager):
        self.api_key = config_manager.get_setting("E2B_API_KEY")
        if not self.api_key:
            print("Warning: E2B_API_KEY not configured - code execution will be disabled")

    async def run_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """Execute code in an E2B sandbox."""
        if not self.api_key:
            raise ValueError("E2B API key not configured")
            
        try:
            template = f"{language}-notebook" if language == "python" else "bash"
            async with e2b.Sandbox(
                template=template,
                api_key=self.api_key,
                timeout=30
            ) as sandbox:
                if language == "python":
                    execution = await sandbox.notebook.exec_cell(code)
                    return {
                        'stdout': execution.logs.stdout,
                        'stderr': execution.logs.stderr,
                        'error': execution.error.name if execution.error else None,
                        'traceback': execution.error.traceback if execution.error else None
                    }
                else:
                    # For non-Python languages
                    proc = await sandbox.process.start_and_wait(code)
                    return {
                        'stdout': proc.stdout,
                        'stderr': proc.stderr,
                        'error': None if proc.exit_code == 0 else f"Exit code {proc.exit_code}",
                        'traceback': None
                    }
                    
        except e2b.APIError as e:
            return {'error': str(e), 'stdout': '', 'stderr': ''}
        except Exception as e:
            return {'error': str(e), 'stdout': '', 'stderr': ''}