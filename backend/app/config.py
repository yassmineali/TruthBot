"""
Configuration settings for TruthBot
"""
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()


class Settings:
    """Application settings"""
    
    # App Configuration
    APP_NAME: str = "TruthBot - Misinformation Analyzer"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Analyze documents and images for misinformation using Gemini AI"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Gemini API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {'.pdf', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png', '.gif'}
    UPLOAD_FOLDER: str = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    
    # CORS Configuration - Allow all common frontend ports
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:5501,http://127.0.0.1:5501,http://localhost:8080,http://127.0.0.1:8080,null"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as list"""
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        # Add wildcard for development
        if self.DEBUG:
            origins.append("*")
        return origins


# Create settings instance
settings = Settings()

# Export commonly used settings
GEMINI_API_KEY = settings.GEMINI_API_KEY
MAX_FILE_SIZE = settings.MAX_FILE_SIZE
ALLOWED_EXTENSIONS = settings.ALLOWED_EXTENSIONS
UPLOAD_FOLDER = settings.UPLOAD_FOLDER
