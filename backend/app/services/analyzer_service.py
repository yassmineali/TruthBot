"""
Main analysis orchestrator service
Coordinates the analysis pipeline
"""
from app.services.gemini_service import GeminiService
from app.services.extractor_service import ExtractorService
from app.services.search_service import SearchService
from app.models import AnalysisResult
import json
import re
import os
from typing import Dict, Any, List, Tuple


class AnalyzerService:
    """Main service that orchestrates the analysis pipeline"""
    
    def __init__(self):
        """Initialize services"""
        self.gemini_service = GeminiService()
        self.extractor_service = ExtractorService()
        self.search_service = SearchService()
        self.use_web_search = bool(os.getenv("SERPER_API_KEY", ""))
    
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
        
        # Step 2: Web search for verification (if enabled)
        search_context = ""
        if self.use_web_search:
            search_results = await self.search_service.verify_claim(content[:200])
            search_context = self.search_service.format_sources_for_analysis(search_results)
        
        # Step 3: Analyze with Gemini (include search results)
        analysis = await self.gemini_service.analyze_text_with_sources(content, search_context)
        
        # Step 4: Parse results
        result = self._parse_analysis(content, analysis, search_context)
        
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
        # Step 1: Web search for verification (if enabled)
        search_context = ""
        if self.use_web_search:
            search_results = await self.search_service.verify_claim(content[:200])
            search_context = self.search_service.format_sources_for_analysis(search_results)
        
        # Step 2: Analyze with Gemini (include search results)
        analysis = await self.gemini_service.analyze_text_with_sources(content, search_context)
        
        # Step 3: Parse results
        result = self._parse_analysis(content, analysis, search_context)
        
        return result
    
    def _parse_analysis(self, content: str, analysis: str, search_context: str = "") -> AnalysisResult:
        """
        Parse Gemini analysis into structured format
        
        Args:
            content: Original content
            analysis: Gemini analysis text
            search_context: Web search results context
            
        Returns:
            Structured AnalysisResult
        """
        # Parse the structured response
        label, confidence = self._extract_reliability(analysis)
        reasons = self._extract_reasons(analysis)
        tips = self._extract_tips(analysis)
        
        # Add search context to analysis details if available
        full_analysis = analysis
        if search_context:
            full_analysis += "\n\n---\n📡 WEB VERIFICATION SOURCES:\n" + search_context
        
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
            analysis_details=full_analysis
        )
    
    def _extract_reliability(self, analysis: str) -> Tuple[str, float]:
        """Extract reliability label and confidence from analysis"""
        analysis_lower = analysis.lower()
        
        # FIRST: Check for NEGATIVE indicators in the FULL text
        # These should take priority to avoid false positives
        
        # Check for SPECULATIVE / UNVERIFIABLE content
        if any(phrase in analysis_lower for phrase in [
            'speculative', 'speculation', 'cannot be verified', 'unverifiable',
            'no credible evidence', 'lacks any factual basis', 'unfounded',
            'no evidence', 'lacks evidence', 'not based on facts',
            'potentially defamatory', 'defamatory', 'rumor', 'rumors',
            'innuendo', 'malicious', 'cannot be verified because',
            'dismissing it as', 'unfounded speculation'
        ]):
            return "needs_verification", 0.70
        
        # Check for POTENTIALLY FALSE indicators
        if any(phrase in analysis_lower for phrase in [
            'potentially false', 'is false', 'appears false', 'likely false',
            'misinformation', 'disinformation', 'fake', 'hoax', 'fabricated',
            'not true', 'untrue', 'debunked', 'false claim', 'conspiracy'
        ]):
            return "potentially_false", 0.85
        
        # Check for UNRELIABLE indicators  
        if any(phrase in analysis_lower for phrase in [
            'unreliable', 'not reliable', 'cannot be trusted', 'untrustworthy',
            'no credible sources', 'spread rumors'
        ]):
            return "potentially_false", 0.75
        
        # Check for DOUBTFUL indicators
        if any(phrase in analysis_lower for phrase in [
            'doubtful', 'questionable', 'suspicious', 'misleading',
            'partially true', 'mixed', 'some truth', 'lacks credibility',
            'political bias', 'personal animosity', 'damage reputation'
        ]):
            return "doubtful", 0.65
        
        # NOW check for POSITIVE indicators (only if no negative found)
        
        # Check for clearly RELIABLE content
        if any(phrase in analysis_lower for phrase in [
            'is reliable', 'appears reliable', 'highly reliable',
            'is accurate', 'appears accurate', 'is credible',
            'is true', 'this is true', 'factually correct',
            'well-established fact', 'universally accepted', 'universally recognized',
            'definitive answer', 'confirmed fact', 'verified fact',
            'no factual errors', 'there are no factual errors', 
            'inherently verifiable', 'established scientific',
            'fundamental aspect', 'basic fact', 'scientifically accurate',
            'common knowledge', 'widely accepted'
        ]):
            return "reliable", 0.85
        
        # Check for NEEDS VERIFICATION 
        if any(phrase in analysis_lower for phrase in [
            'needs verification', 'requires verification', 'unverified claim',
            'insufficient evidence', 'unclear', 'need more context'
        ]):
            return "needs_verification", 0.55
        
        # Default fallback - if we can't determine, it needs verification
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
