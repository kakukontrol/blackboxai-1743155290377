import logging
from fastapi import FastAPI, HTTPException
from app.integrations.astra_client import AstraDBClient
from app.storage.vector_store import QdrantVectorStore
from app.core.embeddings import EmbeddingGenerator
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import uvicorn
from datetime import datetime
from app.core.config import ConfigManager
from app.storage.chat_history import ChatHistoryManager
from app.services.ai_service import AIServiceManager
from app.plugins.base import PluginContext
from app.plugins.manager import PluginManager
from app.api.history_routes import router as history_router
from app.api.ai_routes import router as ai_router

# Initialize services
config_manager = ConfigManager()
chat_history_manager = ChatHistoryManager()
ai_service_manager = AIServiceManager(config_manager)

# Create FastAPI application
app = FastAPI(
    title="PersonaChat API",
    description="Backend API for PersonaChat application", 
    version="1.0.0"
)
# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    try:
        await vector_store.initialize(config_manager)
        await astra_client.connect()
    except Exception as e:
        logging.error(f"Startup initialization failed: {e}")
        raise

# Cleanup on shutdown
@app.on_event("shutdown") 
async def shutdown_event():
    await astra_client.disconnect()

class PluginContext:
    """Context object providing access to core application managers."""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        ai_service_manager: AIServiceManager,
        chat_history_manager: ChatHistoryManager,
        vector_store: VectorStoreInterface,
        embedding_generator: EmbeddingGenerator,
        astra_client: AstraDBClient
    ):
        self.config_manager = config_manager
        self.ai_service_manager = ai_service_manager
        self.chat_history_manager = chat_history_manager
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.astra_client = astra_client

# Include routers
app.include_router(history_router)
app.include_router(ai_router)

# Request/Response Models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    provider: str = "groq"  # Default provider
    model: str = "llama3-8b-8192"  # Default model

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

@app.get("/")
async def root():
    """Root endpoint that returns a welcome message"""
    return {"message": "PersonaChat Backend v1.0 Running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Chat endpoint that uses AI service manager with plugin support."""
=======
from app.services.rag_service import perform_rag_search

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Chat endpoint that uses AI service manager with plugin support and optional RAG."""
>>>>>>> REPLACE
Your changes have NOT been applied.Read the file contents again and provide proper matching lines.
----

</error>

[edit_file for 'personachat/backend/app/main.py'] Result:

The tool execution failed with the following error:
<error>
Error writing file: {"name":"Error","message":"","stack":"Error: \n\tat k9.presentAssistantMessage (/root/.vscode-server/extensions/blackboxapp.blackboxagent-2.9.42/dist/extension.js:3156:1229)"}
</error>

Tool [edit_file] was not executed because a tool has already been used in this message. Only one tool may be used per message. You must assess the first tool's result before proceeding to use the next tool.

<environment_details>
# VSCode Visible Files
../../../opt/vscodium/main.py
personachat/backend/app/main.py

# VSCode Open Tabs
personachat/backend/app/__init__.py
personachat/backend/app/api/__init__.py
personachat/backend/app/api/deps.py
personachat/backend/app/core/__init__.py
personachat/backend/app/core/security.py
personachat/backend/app/models/__init__.py
personachat/backend/app/services/__init__.py
personachat/backend/app/storage/__init__.py
personachat/backend/app/plugins/__init__.py
personachat/backend/app/integrations/__init__.py
personachat/backend/plugins_available/__init__.py
personachat/backend/run_server.py
personachat/frontend/app/__init__.py
personachat/frontend/app/widgets/__init__.py
personachat/frontend/app/widgets/chat_widget.py
personachat/frontend/app/widgets/settings_widget.py
personachat/frontend/app/dialogs/__init__.py
personachat/frontend/app/assets/__init__.py
personachat/frontend/app/assets/styles/__init__.py
personachat/frontend/app/assets/styles/light.qss
personachat/frontend/app/assets/styles/dark.qss
personachat/README.md
personachat/LICENSE
personachat/.gitignore
personachat/backend/.env.example
personachat/frontend/requirements.txt
personachat/frontend/run_ui.py
personachat/backend/app/core/config.py
personachat/backend/app/storage/chat_history.py
personachat/backend/app/api/history_routes.py
personachat/backend/app/services/ai_service.py
personachat/backend/app/api/ai_routes.py
personachat/frontend/app/api_client.py
personachat/frontend/app/main_window.py
personachat/backend/plugins_available/simple_command_plugin.py
personachat/backend/app/plugins/manager.py
personachat/backend/app/storage/vector_store.py
personachat/backend/app/core/embeddings.py
personachat/backend/app/plugins/base.py
personachat/backend/app/services/rag_service.py
</environment_details>

Given the persistent issues with editing files, I'll provide the complete updated version of the /chat endpoint in main.py that you can manually implement:

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Chat endpoint that uses AI service manager with plugin support and optional RAG."""
    # Get or create conversation
    conversation_id = chat_message.conversation_id
    if not conversation_id:
        conversation_id = chat_history_manager.create_conversation()
    
    # Get previous messages (last 10)
    history = chat_history_manager.get_messages(conversation_id, limit=10)
    
    # Prepare messages for AI
    messages = [
        {"role": msg["role"], "content": msg["content"]} 
        for msg in history
    ]
    
    # Process input through plugins
    process_context = {
        "conversation_id": conversation_id,
        "provider": chat_message.provider,
        "model": chat_message.model
    }
    user_message = await plugin_manager.run_process_input_hooks(
        chat_message.message,
        process_context
    )
    
    # Check for RAG trigger
    rag_context = ""
    if user_message.startswith("/rag "):
        rag_query = user_message[5:]  # Remove the /rag trigger
        rag_context = await perform_rag_search(
            rag_query,
            vector_store,
            embedding_generator
        )
        user_message = rag_query  # Use the query without trigger for the actual message
    
    messages.append({"role": "user", "content": user_message})
    
    # Add RAG context if available
    if rag_context:
        messages.insert(-1, {  # Insert before the user message
            "role": "system",
            "content": f"Use the following context to answer the user's question:\n{rag_context}"
        })
    
    # Check if AI processing should be bypassed
    if process_context.get('bypass_ai', False):
        chat_history_manager.add_message(
            conversation_id,
            "user",
            user_message
        )
        return ChatResponse(
            response=user_message,
            conversation_id=conversation_id
        )
    
    try:
        # Call AI service
        ai_content = await ai_service_manager.call_ai(
            provider_name=chat_message.provider,
            model=chat_message.model,
            messages=messages,
            temperature=0.7
        )
        
        # Process output through plugins
        ai_content = await plugin_manager.run_process_output_hooks(
            ai_content,
            process_context
        )
        
        # Save messages to history
        chat_history_manager.add_message(
            conversation_id,
            "user",
            user_message
        )
        chat_history_manager.add_message(
            conversation_id,
            "ai",
            ai_content,
            model_used=chat_message.model
        )
        
        return ChatResponse(
            response=ai_content,
            conversation_id=conversation_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Configure and start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    logger.info("Server started on http://0.0.0.0:8000")