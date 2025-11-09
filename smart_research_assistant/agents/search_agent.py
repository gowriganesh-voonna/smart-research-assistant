# agents/search_agent.py
import os
import uuid
from typing import Dict, Any, List
from models.state_schema import ResearchState

def _tavily_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Perform Tavily search with better error handling."""
    try:
        # Try to use Tavily directly first
        from tavily import Tavily
        tavily_client = Tavily(api_key=os.getenv("TAVILY_API_KEY","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"))
        results = tavily_client.search(query=query, max_results=max_results)
        
        docs = []
        for result in results.get("results", []):
            docs.append({
                "id": str(uuid.uuid4())[:8],
                "title": result.get("title", query),
                "url": result.get("url", ""),
                "snippet": result.get("content", "")[:200],
                "raw_content": result.get("content", ""),
                "source_domain": result.get("url", "").split("/")[2] if result.get("url") else "unknown"
            })
        
        if docs:
            print(f"[SEARCH] Found {len(docs)} real documents from Tavily")
            return docs
            
    except Exception as e:
        print(f"[SEARCH WARNING] Tavily failed: {e}")

    # Fallback to LangChain Tavily
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        tavily_tool = TavilySearchResults(max_results=max_results)
        results = tavily_tool.invoke(query)
        
        docs = []
        for result in results:
            if isinstance(result, dict):
                docs.append({
                    "id": str(uuid.uuid4())[:8],
                    "title": result.get("title", query),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", result.get("content", "")[:200]),
                    "raw_content": result.get("content", result.get("snippet", "")),
                    "source_domain": result.get("url", "").split("/")[2] if result.get("url") else "unknown"
                })
        
        if docs:
            print(f"[SEARCH] Found {len(docs)} documents via LangChain Tavily")
            return docs
            
    except Exception as e:
        print(f"[SEARCH ERROR] All search methods failed: {e}")

    # Final fallback - minimal simulated data
    print("[SEARCH] Using minimal simulated data as fallback")
    return [{
        "id": "sim_1",
        "title": f"Research on {query}",
        "url": "https://example.com/simulated",
        "snippet": f"Simulated content for {query}. Please check your Tavily API key.",
        "raw_content": f"This is simulated content for the topic: {query}. In a real deployment, this would contain actual research content from web sources.",
        "source_domain": "simulated.com"
    }]

def search_agent(state: ResearchState) -> dict:
    """Main search node for LangGraph."""
    query = state.get("topic_query", "").strip()
    if not query:
        return {"raw_documents": []}

    docs = _tavily_search(query, max_results=5)
    print(f"[SEARCH AGENT] Processed query: '{query}', found {len(docs)} documents")
    
    return {"raw_documents": docs}