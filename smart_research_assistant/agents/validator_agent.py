# agents/validator_agent.py
from typing import Dict, Any
from models.state_schema import ResearchState

def validator_agent(state: ResearchState) -> Dict[str, Any]:
    """Validate analysis results and document quality."""
    analysis = state.get("analysis_result", {})
    docs = state.get("raw_documents", [])
    
    # Basic validation checks
    validation_results = {
        "has_sufficient_sources": len(docs) >= 3,
        "has_key_themes": len(analysis.get("themes", [])) > 0,
        "document_quality": "good" if len(docs) > 2 else "poor",
        "source_count": len(docs),
        "theme_count": len(analysis.get("themes", [])),
        "recommendations": []
    }
    
    # Add recommendations based on validation
    if len(docs) < 2:
        validation_results["recommendations"].append("Consider expanding search with more specific terms")
    
    if not analysis.get("themes"):
        validation_results["recommendations"].append("Analysis may need deeper processing")
    
    if len(docs) >= 5:
        validation_results["recommendations"].append("Excellent source diversity")
    
    print(f"[VALIDATOR] Validated {len(docs)} sources, {len(analysis.get('themes', []))} themes")
    
    return {"validation_result": validation_results}