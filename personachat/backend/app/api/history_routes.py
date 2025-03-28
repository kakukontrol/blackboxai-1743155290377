from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.storage.chat_history import ChatHistoryManager

router = APIRouter(prefix="/history", tags=["history"])
chat_history_manager = ChatHistoryManager()

class ConversationListItem(BaseModel):
    id: int
    title: Optional[str]
    created_at: str

class MessageItem(BaseModel):
    id: int
    role: str
    content: str
    timestamp: str
    model_used: Optional[str]
    metadata: Optional[dict]

@router.get("/", response_model=List[ConversationListItem])
async def list_conversations():
    """List all conversations."""
    return chat_history_manager.list_conversations()

@router.post("/", response_model=ConversationListItem)
async def create_conversation(title: Optional[str] = None):
    """Create a new conversation."""
    conv_id = chat_history_manager.create_conversation(title)
    return {
        "id": conv_id,
        "title": title,
        "created_at": datetime.now().isoformat()
    }

@router.get("/{conversation_id}", response_model=List[MessageItem])
async def get_conversation_messages(
    conversation_id: int, 
    limit: Optional[int] = None
):
    """Get messages for a conversation."""
    messages = chat_history_manager.get_messages(conversation_id, limit)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return messages

@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: int):
    """Delete a conversation."""
    if not chat_history_manager.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")

@router.put("/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: int, 
    title: str
):
    """Update a conversation's title."""
    if not chat_history_manager.update_conversation_title(conversation_id, title):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Title updated successfully"}