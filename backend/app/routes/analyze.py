"""
API routes for analysis endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Request
from app.services.analyzer_service import AnalyzerService
from app.models import AnalysisRequest, AnalysisResult, FileUploadResponse
from app.utils.file_handler import FileHandler
import uuid
import json
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["analysis"])
analyzer_service = AnalyzerService()
file_handler = FileHandler()


@router.post("/analyze")
async def analyze(request: Request):
    """
    Unified analyze endpoint for both text and image
    Handles both JSON (text) and FormData (image)
    
    Returns:
        AnalysisResult with analysis
    """
    try:
        content_type = request.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            # Handle JSON payload for text analysis
            body = await request.json()
            request_type = body.get('type')
            
            if request_type == 'text':
                content = body.get('content')
                if not content:
                    raise HTTPException(status_code=400, detail="Content is required for text analysis")
                result = await analyzer_service.analyze_text(content)
                return result
            else:
                raise HTTPException(status_code=400, detail="Type must be 'text' or 'image'")
        
        elif 'multipart/form-data' in content_type:
            # Handle FormData for image analysis
            form_data = await request.form()
            request_type = form_data.get('type')
            file = form_data.get('file')
            
            if request_type == 'image':
                if not file:
                    raise HTTPException(status_code=400, detail="File is required for image analysis")
                
                # Validate file
                if not file_handler.is_allowed_file(file.filename):
                    raise HTTPException(status_code=400, detail="File type not allowed")
                
                # Save file
                file_id = str(uuid.uuid4())
                file_path = file_handler.save_file(file, file_id)
                
                # Analyze the image
                result = await analyzer_service.analyze_image(file_path)
                
                # Clean up file after analysis
                try:
                    file_handler.delete_file(file_id)
                except:
                    pass
                
                return result
            else:
                raise HTTPException(status_code=400, detail="Type must be 'text' or 'image'")
        else:
            raise HTTPException(status_code=400, detail="Invalid content type")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        logger.info(f"📁 File upload received: {file.filename}")
        logger.info(f"   Content-Type: {file.content_type}")
        
        # Validate file
        if not file_handler.is_allowed_file(file.filename):
            logger.error(f"   ❌ File type not allowed: {file.filename}")
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Save file
        file_id = str(uuid.uuid4())
        logger.info(f"   💾 Saving file with ID: {file_id}")
        file_path = file_handler.save_file(file, file_id)
        logger.info(f"   ✅ File saved to: {file_path}")
        
        # Get file extension
        file_ext = Path(file.filename).suffix.lower()[1:]
        logger.info(f"   📄 File extension: {file_ext}")
        
        # Analyze the file directly
        if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            logger.info(f"   🖼️ Analyzing as image...")
            result = await analyzer_service.analyze_image(file_path)
        else:
            logger.info(f"   📝 Extracting text and analyzing...")
            result = await analyzer_service.analyze_file(file_path, file_ext)
        
        logger.info(f"   ✅ Analysis complete: {result.label} ({result.confidence})")
        
        # Clean up file after analysis
        try:
            file_handler.delete_file(file_id)
            logger.info(f"   🗑️ Temporary file cleaned up")
        except:
            pass
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"   ❌ Error during file analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
