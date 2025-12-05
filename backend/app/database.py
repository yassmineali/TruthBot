"""
Database module for storing conversation history
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Database file location
DB_PATH = Path(__file__).parent.parent / "conversations.db"


class Database:
    """SQLite database handler for conversation history"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT,
                filename TEXT,
                result_label TEXT,
                result_confidence REAL,
                result_explanation TEXT,
                result_details TEXT,
                created_at TEXT NOT NULL,
                CONSTRAINT valid_type CHECK (type IN ('text', 'file'))
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON conversations(created_at DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def save_conversation(
        self,
        conv_type: str,
        content: Optional[str] = None,
        filename: Optional[str] = None,
        result: Dict = None
    ) -> int:
        """
        Save a conversation to the database
        
        Args:
            conv_type: Type of content ('text' or 'file')
            content: Text content (for text analysis)
            filename: Filename (for file analysis)
            result: Analysis result dictionary
        
        Returns:
            ID of the created conversation
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Extract result data
        result_label = result.get('label') if result else None
        result_confidence = result.get('confidence') if result else None
        result_explanation = result.get('explanation') if result else None
        result_details = json.dumps(result.get('details', [])) if result else None
        
        cursor.execute("""
            INSERT INTO conversations (
                type, content, filename,
                result_label, result_confidence, result_explanation, result_details,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            conv_type,
            content,
            filename,
            result_label,
            result_confidence,
            result_explanation,
            result_details,
            datetime.utcnow().isoformat()
        ))
        
        conv_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return conv_id
    
    def get_conversations(
        self,
        limit: int = 50,
        offset: int = 0,
        conv_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get conversations from the database
        
        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            conv_type: Filter by type ('text' or 'file')
        
        Returns:
            List of conversation dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM conversations"
        params = []
        
        if conv_type:
            query += " WHERE type = ?"
            params.append(conv_type)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conversations = []
        for row in rows:
            conv = dict(row)
            # Parse JSON details
            if conv.get('result_details'):
                try:
                    conv['result_details'] = json.loads(conv['result_details'])
                except json.JSONDecodeError:
                    conv['result_details'] = []
            conversations.append(conv)
        
        conn.close()
        return conversations
    
    def get_conversation_by_id(self, conv_id: int) -> Optional[Dict]:
        """
        Get a specific conversation by ID
        
        Args:
            conv_id: Conversation ID
        
        Returns:
            Conversation dictionary or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
        row = cursor.fetchone()
        
        if row:
            conv = dict(row)
            # Parse JSON details
            if conv.get('result_details'):
                try:
                    conv['result_details'] = json.loads(conv['result_details'])
                except json.JSONDecodeError:
                    conv['result_details'] = []
            conn.close()
            return conv
        
        conn.close()
        return None
    
    def delete_conversation(self, conv_id: int) -> bool:
        """
        Delete a conversation
        
        Args:
            conv_id: Conversation ID
        
        Returns:
            True if deleted, False if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_stats(self) -> Dict:
        """
        Get conversation statistics
        
        Returns:
            Dictionary with statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM conversations")
        total = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM conversations 
            GROUP BY type
        """)
        type_counts = {row['type']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT result_label, COUNT(*) as count 
            FROM conversations 
            WHERE result_label IS NOT NULL
            GROUP BY result_label
        """)
        label_counts = {row['result_label']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total': total,
            'by_type': type_counts,
            'by_label': label_counts
        }


# Singleton instance
db = Database()
