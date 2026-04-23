#!/usr/bin/env python3
"""
AI-Powered Keyword Extraction for ResearchBook
Uses LightLLM to extract research keywords from titles, abstracts, and content
"""

import requests
import json
import os
from typing import List, Dict, Any

class AIKeywordExtractor:
    def __init__(self, ai_base_url: str = None):
        """Initialize the AI keyword extractor"""
        self.ai_base_url = ai_base_url or os.getenv("LIGHTLLM_BASE_URL", "https://localhost:4000")
        # Use environment variables for credentials
        self.llm_key = os.getenv("LIGHTLLM_API_KEY")
        self.llm_model = os.getenv("LIGHTLLM_MODEL", "claude-sonnet-4")
    # Api integration  
    def ai_query(self, prompt: str) -> str:
        """Query the LightLLM API using the same format as the main system"""
        headers = {
            "Authorization": f"Bearer {self.llm_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                f"{self.ai_base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"AI Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"AI Error: {e}"
    # Prompt engineering / LLM pipeline
    def extract_keywords_from_publications(self, publications: List[Dict[str, Any]]) -> List[str]:
        """
        Extract research keywords from publication titles and abstracts using AI
        
        Args:
            publications: List of publication dicts with 'name' (title) and optionally 'abstract'
            
        Returns:
            List of extracted keywords
        """
        if not publications:
            return []
        
        # Prepare publication data for AI analysis
        pub_texts = []
        for pub in publications:
            title = pub.get('name', '').strip()
            abstract = pub.get('abstract', '').strip()
            
            if title:
                if abstract and len(abstract) > 50:  # Only include substantial abstracts
                    pub_texts.append(f"Title: {title}\nAbstract: {abstract}")
                else:
                    pub_texts.append(f"Title: {title}")
        
        if not pub_texts:
            return []
        
        # Limit to avoid too long prompts
        pub_sample = pub_texts[:5]  # Use first 5 publications
        
        # Create AI prompt for keyword extraction
        prompt = f"""
Analyze the following academic publications and extract the most important research keywords and concepts.

Publications:
{chr(10).join([f"{i+1}. {text}" for i, text in enumerate(pub_sample)])}

Extract 10-15 specific research keywords that best describe the research focus, methods, and domain. Focus on:
- Technical terms and concepts
- Research methodologies  
- Domain-specific terminology
- Key technologies mentioned
- Research areas

Provide ONLY a comma-separated list of keywords, no explanations:
"""

        # Get AI response
        ai_response = self.ai_query(prompt)
        
        if ai_response.startswith("AI Error"):
            print(f"⚠️ AI keyword extraction failed: {ai_response}")
            return self._fallback_keyword_extraction(publications)
        
        # Parse AI response
        keywords = self._parse_keyword_response(ai_response)
        print(f"🤖 AI extracted {len(keywords)} keywords from {len(publications)} publications")
        
        return keywords
    
    def extract_keywords_from_thesis_data(self, thesis_data: List[Dict[str, Any]]) -> List[str]:
        """
        Extract research keywords from thesis titles and existing keywords using AI
        
        Args:
            thesis_data: List of thesis dicts with 'title' and optionally 'keywords'
            
        Returns:
            List of extracted keywords
        """
        if not thesis_data:
            return []
        
        # Collect thesis information
        thesis_texts = []
        existing_keywords = []
        
        for thesis in thesis_data:
            title = thesis.get('title', '').strip() if thesis.get('title') else ''
            keywords = thesis.get('keywords', [])
            
            if title:
                thesis_texts.append(f"Thesis: {title}")
            
            if keywords and isinstance(keywords, list):
                existing_keywords.extend(keywords)
        
        # Combine existing keywords with AI-extracted ones from titles
        all_keywords = list(set(existing_keywords))  # Start with existing
        
        if thesis_texts:
            # Create AI prompt for thesis analysis
            prompt = f"""
Analyze the following thesis titles and extract additional research keywords and concepts.

Thesis Titles:
{chr(10).join([f"{i+1}. {text}" for i, text in enumerate(thesis_texts)])}

Existing Keywords: {', '.join(existing_keywords[:10]) if existing_keywords else 'None'}

Extract 5-10 additional specific research keywords that complement the existing ones. Focus on:
- Research domains and fields
- Technical methodologies
- Key concepts and theories
- Application areas

Provide ONLY a comma-separated list of NEW keywords (avoid duplicating existing ones):
"""

            # Get AI response
            ai_response = self.ai_query(prompt)
            
            if not ai_response.startswith("AI Error"):
                new_keywords = self._parse_keyword_response(ai_response)
                all_keywords.extend(new_keywords)
                print(f" AI extracted {len(new_keywords)} additional keywords from thesis data")
        
        return list(set(all_keywords))  # Remove duplicates
    
    def _parse_keyword_response(self, ai_response: str) -> List[str]:
        """Parse AI response to extract clean keywords"""
        if not ai_response or ai_response.startswith("AI Error"):
            return []
        
        # Clean up the response
        response = ai_response.strip()
        
        # Remove common AI response prefixes
        prefixes_to_remove = [
            "Keywords:", "Research keywords:", "Here are the keywords:",
            "The keywords are:", "Extracted keywords:"
        ]
        
        for prefix in prefixes_to_remove:
            if response.lower().startswith(prefix.lower()):
                response = response[len(prefix):].strip()
        
        # Split by commas and clean
        keywords = []
        if response:
            raw_keywords = response.split(',')
            for kw in raw_keywords:
                clean_kw = kw.strip().strip('"').strip("'").strip()
                if clean_kw and len(clean_kw) > 2:  # Minimum length filter
                    keywords.append(clean_kw)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                seen.add(kw_lower)
                unique_keywords.append(kw)
        
        return unique_keywords[:15]  # Limit to 15 keywords
    
    def _fallback_keyword_extraction(self, publications: List[Dict[str, Any]]) -> List[str]:
        """Fallback keyword extraction without AI"""
        keywords = []
        
        for pub in publications:
            title = pub.get('name', '').lower()
            
            # Simple keyword extraction from titles
            tech_terms = [
                'machine learning', 'artificial intelligence', 'deep learning',
                'algorithm', 'optimization', 'simulation', 'analysis',
                'experimental', 'theoretical', 'computational',
                'model', 'system', 'method', 'approach', 'technique',
                'data', 'network', 'control', 'design', 'development'
            ]
            
            for term in tech_terms:
                if term in title:
                    keywords.append(term)
        
        return list(set(keywords))  # Remove duplicates


def test_ai_keyword_extraction():
    """Test the AI keyword extraction system"""
    extractor = AIKeywordExtractor()
    
    print(" TESTING AI KEYWORD EXTRACTION")
    print("=" * 40)
    
    # Test with sample publications
    sample_publications = [
        {
            "name": "An experimental investigation of the flow in the spiral casing and distributor of the Hölleforsen Kaplan turbine model",
            "abstract": "This study presents experimental investigations of the flow characteristics in turbine components using advanced measurement techniques."
        },
        {
            "name": "Machine learning approaches for predictive maintenance in industrial systems",
            "abstract": ""
        }
    ]
    
    print("📚 Sample Publications:")
    for i, pub in enumerate(sample_publications, 1):
        print(f"{i}. {pub['name']}")
    
    # Extract keywords
    keywords = extractor.extract_keywords_from_publications(sample_publications)
    
    print(f"\n Extracted Keywords ({len(keywords)}):")
    for i, kw in enumerate(keywords, 1):
        print(f"{i}. {kw}")
    
    # Test with thesis data
    sample_thesis = [
        {
            "title": "Deep learning for autonomous vehicle navigation",
            "keywords": ["autonomous vehicles", "navigation"]
        }
    ]
    
    thesis_keywords = extractor.extract_keywords_from_thesis_data(sample_thesis)
    print(f"\n Thesis Keywords ({len(thesis_keywords)}):")
    for i, kw in enumerate(thesis_keywords, 1):
        print(f"{i}. {kw}")


if __name__ == "__main__":
    test_ai_keyword_extraction()




# 1) API Integrations – ai_query()
# Implements REST calls with auth, JSON, and error handling — same pattern for Slack/Figma/GitLab APIs.

# 2) Prompt Engineering – extract_keywords_*
# Uses structured prompts and temperature control for consistent, parseable LLM outputs.

# 3) Data Parsing – _parse_keyword_response()
# Cleans and normalizes AI text into structured lists, just like mapping design tokens.

# 4) Robustness & Fallbacks – error handling + _fallback_keyword_extraction()
# Handles API failures gracefully and maintains output reliability.

# 5) Resource Control – pub_sample[:5], max_tokens=200
# Implements batching and token limits—key for scalable API and LLM pipelines.

# 6) Modular Design – AIKeywordExtractor class
# Separates integration, logic, parsing, and fallback—mirrors service-based Ericsson architecture.