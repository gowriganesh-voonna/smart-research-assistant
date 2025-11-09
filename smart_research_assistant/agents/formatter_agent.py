# agents/formatter_agent.py
from typing import Dict, Any
from models.state_schema import ResearchState
from utils.pdf_utils import generate_pdf
import traceback

def formatter_agent(state: ResearchState) -> Dict[str, Any]:
    """Format final output and generate PDF report with comprehensive error handling."""
    try:
        topic = state.get("topic_query", "")
        summary = state.get("final_summary", "")
        analysis = state.get("analysis_result", {})
        docs = state.get("raw_documents", [])
        validation = state.get("validation_result", {})
        
        print(f"[FORMATTER] Starting PDF generation for: {topic}")
        print(f"[FORMATTER] Summary length: {len(summary)} characters")
        print(f"[FORMATTER] Documents count: {len(docs)}")
        print(f"[FORMATTER] Analysis keys: {analysis.keys()}")
        print(f"[FORMATTER] Validation keys: {validation.keys()}")
        
        # Generate formatted PDF
        pdf_path = generate_pdf(topic, summary, analysis, docs, validation)
        
        # Prepare final formatted output
        formatted_output = {
            "formatted_report": {
                "title": f"Research Report: {topic}",
                "summary_length": len(summary),
                "key_findings": analysis.get("themes", []),
                "keywords": analysis.get("keywords", [])[:10],
                "sources_used": len(docs),
                "validation_status": validation.get("document_quality", "unknown"),
                "validation_score": "High" if validation.get("has_sufficient_sources") else "Medium"
            },
            "pdf_path": pdf_path
        }
        
        print(f"[FORMATTER] Successfully generated PDF at: {pdf_path}")
        return formatted_output
        
    except Exception as e:
        print(f"[FORMATTER ERROR] PDF generation failed: {e}")
        print(f"[FORMATTER ERROR] Traceback: {traceback.format_exc()}")
        
        # Return fallback result without PDF
        return {
            "formatted_report": {
                "title": f"Research Report: {state.get('topic_query', '')}",
                "summary_length": len(state.get("final_summary", "")),
                "key_findings": state.get("analysis_result", {}).get("themes", []),
                "sources_used": len(state.get("raw_documents", [])),
                "validation_status": "error",
                "error": f"PDF generation failed: {str(e)}"
            },
            "pdf_path": ""
        }