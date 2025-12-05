"""
Conversation history routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.database import db

router = APIRouter()


class ConversationCreate(BaseModel):
    """Schema for creating a conversation"""
    type: str
    content: Optional[str] = None
    filename: Optional[str] = None
    result: Optional[Dict] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    id: int
    type: str
    content: Optional[str]
    filename: Optional[str]
    result_label: Optional[str]
    result_confidence: Optional[float]
    result_explanation: Optional[str]
    result_details: Optional[List[str]]
    created_at: str


@router.post("/conversations", response_model=dict)
async def create_conversation(conversation: ConversationCreate):
    """Save a new conversation to the database"""
    try:
        conv_id = db.save_conversation(
            conv_type=conversation.type,
            content=conversation.content,
            filename=conversation.filename,
            result=conversation.result
        )
        return {
            "success": True,
            "id": conv_id,
            "message": "Conversation saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save conversation: {str(e)}")


@router.get("/conversations", response_model=List[dict])
async def get_conversations(
    limit: int = 50,
    offset: int = 0,
    type: Optional[str] = None
):
    """Get conversation history"""
    try:
        conversations = db.get_conversations(limit=limit, offset=offset, conv_type=type)
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversations: {str(e)}")


@router.get("/conversations/{conv_id}", response_model=dict)
async def get_conversation(conv_id: int):
    """Get a specific conversation by ID"""
    try:
        conversation = db.get_conversation_by_id(conv_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")


@router.delete("/conversations/{conv_id}", response_model=dict)
async def delete_conversation(conv_id: int):
    """Delete a conversation"""
    try:
        deleted = db.delete_conversation(conv_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {
            "success": True,
            "message": "Conversation deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")


@router.get("/conversations/stats/summary", response_model=dict)
async def get_conversation_stats():
    """Get conversation statistics"""
    try:
        stats = db.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")
