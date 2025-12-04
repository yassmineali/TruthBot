"""
Gemini AI integration service
Handles communication with Google Gemini API
"""
import google.generativeai as genai
from app.config import GEMINI_API_KEY
from PIL import Image
import io


class GeminiService:
    """Service for interacting with Gemini API"""
    
    def __init__(self):
        """Initialize Gemini with API key"""
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def analyze_text(self, content: str) -> str:
        """
        Analyze text content using Gemini
        
        Args:
            content: Text to analyze
            
        Returns:
            Analysis result from Gemini
        """
        prompt = f"""You are a fact-checking and misinformation detection expert. Analyze the following content for accuracy, misinformation, bias, and reliability.

CONTENT TO ANALYZE:
{content}

Please provide a structured analysis with the following sections:

## Reliability Assessment
[State if the content is: reliable, doubtful, needs_verification, or potentially_false]

## Key Findings
- [List the main claims or statements found]
- [Note any factual errors or misleading information]
- [Identify potential biases]

## Reasons for Assessment
- [Explain why you rated it this way]
- [List specific red flags or positive indicators]

## Verification Tips
- [Suggest how to verify this information]
- [Recommend sources to cross-reference]

Be specific and helpful in your analysis."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Analysis could not be completed: {str(e)}. Please verify the content manually through trusted sources."
    
    async def analyze_text_with_sources(self, content: str, search_context: str = "") -> str:
        """
        Analyze text content using Gemini with web search context
        
        Args:
            content: Text to analyze
            search_context: Web search results for verification
            
        Returns:
            Analysis result from Gemini
        """
        # Build prompt with search context if available
        search_section = ""
        if search_context:
            search_section = f"""
## WEB SEARCH RESULTS (Use these to verify the claim):
{search_context}

Use the above web search results to help verify the claim. If fact-checking sources found information about this claim, use that to inform your assessment.
"""
        
        prompt = f"""You are a fact-checking and misinformation detection expert. Analyze the following content for accuracy, misinformation, bias, and reliability.

CONTENT TO ANALYZE:
{content}
{search_section}
Please provide a structured analysis with the following sections:

## Reliability Assessment
[State CLEARLY if the content is: "reliable", "doubtful", "needs_verification", or "potentially_false"]
[Be definitive in your assessment based on available evidence]

## Key Findings
- [List the main claims or statements found]
- [Note any factual errors or misleading information]
- [Identify potential biases]

## Reasons for Assessment
- [Explain why you rated it this way]
- [Reference any fact-check sources if available]
- [List specific red flags or positive indicators]

## Verification Tips
- [Suggest how to verify this information]
- [Recommend sources to cross-reference]

IMPORTANT: 
- For simple factual questions (like "is blue a color"), clearly state it is RELIABLE if true.
- For speculative claims without evidence, state it NEEDS VERIFICATION or is POTENTIALLY FALSE.
- Use the web search results to inform your assessment when available.

Be specific and helpful in your analysis."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Analysis could not be completed: {str(e)}. Please verify the content manually through trusted sources."
    
    async def analyze_image(self, image_path: str) -> str:
        """
        Analyze image using Gemini Vision
        
        Args:
            image_path: Path to image file
            
        Returns:
            Analysis result from Gemini
        """
        prompt = """You are an expert at detecting manipulated, misleading, or fake images. Analyze this image thoroughly.

Please provide a structured analysis with:

## Image Description
[Describe what the image shows]

## Reliability Assessment
[State if the image appears: reliable, doubtful, needs_verification, or potentially_false]

## Signs of Manipulation
- [List any signs of digital manipulation, editing, or AI generation]
- [Note any inconsistencies in lighting, shadows, or proportions]

## Context Concerns
- [Identify if the image could be misleading when taken out of context]
- [Note any concerning elements]

## Verification Tips
- [Suggest how to verify this image's authenticity]
- [Recommend reverse image search or other tools]

Be thorough and specific in your analysis."""
        
        try:
            # Load and process image
            img = Image.open(image_path)
            response = self.vision_model.generate_content([prompt, img])
            return response.text
        except Exception as e:
            return f"Image analysis could not be completed: {str(e)}. Please verify the image manually."
