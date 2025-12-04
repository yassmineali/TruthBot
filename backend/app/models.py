"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class ReliabilityLabel(str, Enum):
    """Labels for content reliability"""
    RELIABLE = "reliable"
    DOUBTFUL = "doubtful"
    NEEDS_VERIFICATION = "needs_verification"
    POTENTIALLY_FALSE = "potentially_false"
    UNKNOWN = "unknown"


class AnalysisRequest(BaseModel):
    """Request model for text analysis"""
    content: str
    file_type: Optional[str] = "text"
    source_url: Optional[str] = None


class AnalysisResult(BaseModel):
    """Analysis result returned to frontend"""
    label: str  # reliable, doubtful, needs_verification, potentially_false, unknown
    confidence: float  # 0.0 to 1.0
    content_preview: str
    reasons: List[str]
    tips: List[str]
    analysis_details: Optional[str] = None


class FileUploadResponse(BaseModel):
    """Response after file upload"""
    status: str
    file_id: str
    file_name: str
    content_preview: str
