import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class ChatHistoryManager:
    """Manages chat history storage using SQLite."""
    
    def __init__(self):
        self.db_path = Path.home() / ".personachat" / "chat_history.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get a new database connection with proper settings."""
        conn = sqlite3.connect(
            str(self.db_path),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self):
        """Initialize the database tables if they don't exist."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'ai', 'system')),
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_used TEXT,
                    metadata TEXT,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()

    def create_conversation(self, title: Optional[str] = None) -> int:
        """Create a new conversation and return its ID."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (title) VALUES (?)",
                (title,)
            )
            conn.commit()
            return cursor.lastrowid

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        model_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message to a conversation."""
        metadata_str = json.dumps(metadata) if metadata else None
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO messages 
                (conversation_id, role, content, model_used, metadata) 
                VALUES (?, ?, ?, ?, ?)""",
                (conversation_id, role, content, model_used, metadata_str)
            )
            conn.commit()

    def get_messages(
        self, 
        conversation_id: int, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get messages for a conversation."""
        query = """
            SELECT * FROM messages 
            WHERE conversation_id = ? 
            ORDER BY timestamp ASC
        """
        params = [conversation_id]
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                message = dict(row)
                if message['metadata']:
                    message['metadata'] = json.loads(message['metadata'])
                messages.append(message)
                
            return messages

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all conversations ordered by creation date."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, created_at 
                FROM conversations 
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and its messages."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def update_conversation_title(
        self, 
        conversation_id: int, 
        title: str
    ) -> bool:
        """Update a conversation's title."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET title = ? WHERE id = ?",
                (title, conversation_id)
            )
            conn.commit()
            return cursor.rowcount > 0