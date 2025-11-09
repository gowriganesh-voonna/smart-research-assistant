# agents/analysis_agent.py
from typing import Dict, Any, List
from models.state_schema import ResearchState
from collections import Counter
import re

def extract_meaningful_themes(texts: List[str], topic: str) -> List[str]:
    """Extract more meaningful themes related to the actual topic."""
    # Combine all text
    full_text = " ".join(texts).lower()
    
    # Remove common stop words and the topic itself
    stop_words = {'the', 'and', 'for', 'with', 'that', 'this', 'from', 'have', 'has', 'been', 'are', 'were', 'their'}
    topic_words = set(topic.lower().split())
    stop_words.update(topic_words)
    
    # Extract meaningful words
    words = re.findall(r"\b[a-zA-Z]{5,}\b", full_text)
    filtered_words = [w for w in words if w not in stop_words]
    
    # Get most common words
    common_words = Counter(filtered_words).most_common(8)
    
    # Convert to meaningful themes
    themes = [word.title() for word, count in common_words if count > 1]
    
    return themes[:5]  # Return top 5 themes

def analyze_agent(state: ResearchState) -> Dict[str, Any]:
    """
    Node: analyze_agent
    Improved analysis with topic context
    """
    docs = state.get("raw_documents", [])
    topic = state.get("topic_query", "")
    all_texts = [d.get("raw_content", "") for d in docs if d.get("raw_content")]

    if not all_texts:
        return {"analysis_result": {
            "keywords": [], 
            "themes": [], 
            "summary": "No content to analyze",
            "num_sources": 0
        }}

    # Extract themes considering the actual topic
    themes = extract_meaningful_themes(all_texts, topic)
    
    # Extract keywords
    words = re.findall(r"\b[a-zA-Z]{4,}\b", " ".join(all_texts).lower())
    common_words = Counter(words).most_common(12)
    keywords = [word for word, count in common_words]

    analysis = {
        "keywords": keywords[:10],
        "themes": themes,
        "num_sources": len(docs),
        "content_quality": "good" if len(all_texts) > 3 else "limited"
    }

    print(f"[ANALYSIS] Found {len(themes)} themes, {len(keywords)} keywords from {len(docs)} sources")
    
    return {"analysis_result": analysis}