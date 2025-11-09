# models/state_schema.py
from typing import TypedDict, List, Dict, Optional, Any

class ResearchState(TypedDict, total=False):
    topic_query: str
    raw_documents: List[Dict[str, Any]]
    analysis_result: Dict[str, Any]
    validation_result: Dict[str, Any]
    final_summary: str
    formatted_report: Dict[str, Any]
    pdf_path: Optional[str]