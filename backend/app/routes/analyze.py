"""
API routes for analysis endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.analyzer_service import AnalyzerService
from app.models import AnalysisRequest, AnalysisResult, FileUploadResponse
from app.utils.file_handler import FileHandler
import uuid
from pathlib import Path

router = APIRouter(tags=["analysis"])
analyzer_service = AnalyzerService()
file_handler = FileHandler()


@router.post("/analyze/text", response_model=AnalysisResult)
async def analyze_text(request: AnalysisRequest):
    """
    Analyze text content for misinformation
    
    Args:
        request: AnalysisRequest with content
        
    Returns:
        AnalysisResult with analysis
    """
    try:
        result = await analyzer_service.analyze_text(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/upload", response_model=AnalysisResult)
async def upload_and_analyze(file: UploadFile = File(...)):
    """
    Upload a file and analyze it directly
    
    Args:
        file: Uploaded file
        
    Returns:
        AnalysisResult with analysis
    """
    try:
        # Validate file
        if not file_handler.is_allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = file_handler.save_file(file, file_id)
        
        # Get file extension
        file_ext = Path(file.filename).suffix.lower()[1:]
        
        # Analyze the file directly
        if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            result = await analyzer_service.analyze_image(file_path)
        else:
            result = await analyzer_service.analyze_file(file_path, file_ext)
        
        # Clean up file after analysis
        try:
            file_handler.delete_file(file_id)
        except:
            pass
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
