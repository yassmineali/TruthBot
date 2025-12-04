"""
Main analysis orchestrator service
Coordinates the analysis pipeline
"""
from app.services.gemini_service import GeminiService
from app.services.extractor_service import ExtractorService
from app.models import AnalysisResult
import json
import re
from typing import Dict, Any, List, Tuple


class AnalyzerService:
    """Main service that orchestrates the analysis pipeline"""
    
    def __init__(self):
        """Initialize services"""
        self.gemini_service = GeminiService()
        self.extractor_service = ExtractorService()
    
    async def analyze_file(self, file_path: str, file_type: str) -> AnalysisResult:
        """
        Analyze a file through the complete pipeline
        
        Args:
            file_path: Path to the file
            file_type: File extension
            
        Returns:
            AnalysisResult with findings
        """
        # Step 1: Extract content
        content = self.extractor_service.extract_text(file_path, file_type)
        
        # Step 2: Analyze with Gemini
        analysis = await self.gemini_service.analyze_text(content)
        
        # Step 3: Parse results
        result = self._parse_analysis(content, analysis)
        
        return result
    
    async def analyze_image(self, file_path: str) -> AnalysisResult:
        """
        Analyze an image through Gemini Vision
        
        Args:
            file_path: Path to image file
            
        Returns:
            AnalysisResult with findings
        """
        # Open image
        with open(file_path, 'rb') as f:
            image_data = f.read()
        
        # Analyze with Gemini Vision
        analysis = await self.gemini_service.analyze_image(file_path)
        
        # Parse results
        result = self._parse_analysis("Image content analysis", analysis)
        
        return result
    
    async def analyze_text(self, content: str) -> AnalysisResult:
        """
        Analyze raw text content
        
        Args:
            content: Text to analyze
            
        Returns:
            AnalysisResult with findings
        """
        # Analyze with Gemini
        analysis = await self.gemini_service.analyze_text(content)
        
        # Parse results
        result = self._parse_analysis(content, analysis)
        
        return result
    
    def _parse_analysis(self, content: str, analysis: str) -> AnalysisResult:
        """
        Parse Gemini analysis into structured format
        
        Args:
            content: Original content
            analysis: Gemini analysis text
            
        Returns:
            Structured AnalysisResult
        """
        # Parse the structured response
        label, confidence = self._extract_reliability(analysis)
        reasons = self._extract_reasons(analysis)
        tips = self._extract_tips(analysis)
        
        return AnalysisResult(
            label=label,
            confidence=confidence,
            content_preview=content[:300] + "..." if len(content) > 300 else content,
            reasons=reasons if reasons else ["Analysis completed. See details below."],
            tips=tips if tips else [
                "Cross-reference with reputable news sources",
                "Check the date and context of the information",
                "Look for primary sources and official statements"
            ],
            analysis_details=analysis
        )
    
    def _extract_reliability(self, analysis: str) -> Tuple[str, float]:
        """Extract reliability label and confidence from analysis"""
        analysis_lower = analysis.lower()
        
        # Check for explicit labels
        if "potentially false" in analysis_lower or "false" in analysis_lower or "misinformation" in analysis_lower:
            return "potentially_false", 0.85
        elif "unreliable" in analysis_lower or "not reliable" in analysis_lower:
            return "potentially_false", 0.75
        elif "doubtful" in analysis_lower or "questionable" in analysis_lower:
            return "doubtful", 0.65
        elif "needs verification" in analysis_lower or "verify" in analysis_lower or "unverified" in analysis_lower:
            return "needs_verification", 0.55
        elif "reliable" in analysis_lower or "credible" in analysis_lower or "accurate" in analysis_lower:
            return "reliable", 0.80
        elif "high reliability" in analysis_lower:
            return "reliable", 0.90
        else:
            return "needs_verification", 0.50
    
    def _extract_reasons(self, analysis: str) -> List[str]:
        """Extract reasons from analysis"""
        reasons = []
        lines = analysis.split('\n')
        
        in_reasons_section = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if any(keyword in line.lower() for keyword in ['reason', 'finding', 'issue', 'concern', 'red flag', 'key claim']):
                in_reasons_section = True
                continue
            
            # Extract bullet points
            if in_reasons_section and (line.startswith('-') or line.startswith('•') or line.startswith('*') or re.match(r'^\d+\.', line)):
                reason = re.sub(r'^[-•*\d.]+\s*', '', line).strip()
                if reason and len(reason) > 10:
                    reasons.append(reason)
                    if len(reasons) >= 5:
                        break
            
            # Stop if we hit a new section
            if in_reasons_section and ':' in line and not line.startswith('-'):
                in_reasons_section = False
        
        return reasons[:5]
    
    def _extract_tips(self, analysis: str) -> List[str]:
        """Extract verification tips from analysis"""
        tips = []
        lines = analysis.split('\n')
        
        in_tips_section = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if any(keyword in line.lower() for keyword in ['recommendation', 'tip', 'suggestion', 'verification']):
                in_tips_section = True
                continue
            
            # Extract bullet points
            if in_tips_section and (line.startswith('-') or line.startswith('•') or line.startswith('*') or re.match(r'^\d+\.', line)):
                tip = re.sub(r'^[-•*\d.]+\s*', '', line).strip()
                if tip and len(tip) > 10:
                    tips.append(tip)
                    if len(tips) >= 4:
                        break
        
        # Default tips if none found
        if not tips:
            tips = [
                "Verify claims through multiple reputable sources",
                "Check the original source and publication date",
                "Look for expert opinions and fact-checker assessments",
                "Consider the context and potential biases"
            ]
        
        return tips[:4]
