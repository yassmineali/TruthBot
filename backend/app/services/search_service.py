"""
Web Search Service for fact verification
Uses Serper.dev API for Google search results
"""
import aiohttp
import os
from typing import List, Dict, Optional
from app.config import settings


class SearchService:
    """Service for web search to verify claims"""
    
    def __init__(self):
        """Initialize search service"""
        self.api_key = os.getenv("SERPER_API_KEY", "")
        self.base_url = "https://google.serper.dev/search"
    
    async def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search the web for information about a claim
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, link, snippet
        """
        if not self.api_key:
            return []
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": num_results
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_results(data)
                    else:
                        print(f"Search API error: {response.status}")
                        return []
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        """Parse search results from Serper API response"""
        results = []
        
        # Parse organic results
        organic = data.get("organic", [])
        for item in organic[:5]:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": self._extract_domain(item.get("link", ""))
            })
        
        # Parse knowledge graph if available
        knowledge_graph = data.get("knowledgeGraph", {})
        if knowledge_graph:
            results.insert(0, {
                "title": knowledge_graph.get("title", ""),
                "link": knowledge_graph.get("website", ""),
                "snippet": knowledge_graph.get("description", ""),
                "source": "Knowledge Graph",
                "is_knowledge_graph": True
            })
        
        # Parse answer box if available
        answer_box = data.get("answerBox", {})
        if answer_box:
            results.insert(0, {
                "title": answer_box.get("title", "Direct Answer"),
                "link": answer_box.get("link", ""),
                "snippet": answer_box.get("snippet", answer_box.get("answer", "")),
                "source": "Google Answer",
                "is_answer_box": True
            })
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return url
    
    async def verify_claim(self, claim: str) -> Dict:
        """
        Verify a claim by searching for it
        
        Args:
            claim: The claim to verify
            
        Returns:
            Dict with search results and verification context
        """
        # Create search queries
        queries = [
            f'"{claim}" fact check',
            f'{claim} true or false',
            claim
        ]
        
        all_results = []
        fact_check_results = []
        
        for query in queries[:2]:  # Limit API calls
            results = await self.search(query, num_results=3)
            for result in results:
                # Check if it's from a fact-checking source
                source = result.get("source", "").lower()
                if any(fc in source for fc in [
                    "snopes", "politifact", "factcheck.org", 
                    "reuters", "ap news", "bbc", "wikipedia"
                ]):
                    fact_check_results.append(result)
                else:
                    all_results.append(result)
        
        return {
            "fact_check_sources": fact_check_results[:3],
            "other_sources": all_results[:5],
            "total_results": len(fact_check_results) + len(all_results)
        }
    
    def format_sources_for_analysis(self, search_results: Dict) -> str:
        """Format search results for inclusion in AI analysis"""
        lines = []
        
        fact_checks = search_results.get("fact_check_sources", [])
        if fact_checks:
            lines.append("\n## Fact-Check Sources Found:")
            for result in fact_checks:
                lines.append(f"- **{result['source']}**: {result['snippet'][:200]}")
        
        other = search_results.get("other_sources", [])
        if other:
            lines.append("\n## Related Web Sources:")
            for result in other[:3]:
                lines.append(f"- **{result['source']}**: {result['snippet'][:150]}")
        
        return "\n".join(lines) if lines else ""
