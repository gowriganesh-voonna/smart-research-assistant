# main.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents.search_agent import search_agent
from agents.analysis_agent import analyze_agent
from agents.validator_agent import validator_agent
from agents.summarizer_agent import summarizer_agent
from agents.formatter_agent import formatter_agent
from models.state_schema import ResearchState
import os
os.environ["TAVILY_API_KEY"] = "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"


def check_environment():
    """Check if required API keys are available."""
    tavily_key = os.getenv("TAVILY_API_KEY","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")
    gemini_key = os.getenv("GEMINI_API_KEY","AIzaSyDgIuCfgQnqE4l_J4EX-ClysACAw7cNq8s")
    
    if not tavily_key or tavily_key.startswith("tvly-dev-"):
        print("⚠️  WARNING: Using simulated/search-limited mode for Tavily")
        print("   Get a real API key from: https://app.tavily.com")
    else:
        print("✅ Tavily API key is configured")
    
    if not gemini_key or gemini_key == "AIzaSyDgIuCfgQnqE4l_J4EX-ClysACAw7cNq8s":
        print("⚠️  WARNING: Using default Gemini API key - may not work")
        print("   Get your API key from: https://aistudio.google.com/app/apikey")
    else:
        print("✅ Gemini API key is configured")

def build_research_workflow():
    """Build the complete Smart Research Assistant workflow using LangGraph."""
    workflow = StateGraph(ResearchState)

    # Define all workflow nodes
    workflow.add_node("search_agent", search_agent)
    workflow.add_node("analyze_agent", analyze_agent)
    workflow.add_node("validator_agent", validator_agent)
    workflow.add_node("summarize_agent", summarizer_agent)
    workflow.add_node("formatter_agent", formatter_agent)

    # Define the complete workflow with proper edges
    workflow.set_entry_point("search_agent")
    workflow.add_edge("search_agent", "analyze_agent")
    workflow.add_edge("analyze_agent", "validator_agent")
    workflow.add_edge("validator_agent", "summarize_agent")
    workflow.add_edge("summarize_agent", "formatter_agent")
    workflow.add_edge("formatter_agent", END)

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def run_research_workflow(topic_query: str):
    """Execute the complete LangGraph workflow."""
    app = build_research_workflow()
    
    # Proper LangGraph invocation with state management
    config = {"configurable": {"thread_id": "user_session_123"}}
    
    print(f"[WORKFLOW] Starting research workflow for: '{topic_query}'")
    
    result = app.invoke(
        {"topic_query": topic_query},
        config=config
    )
    
    print(f"[WORKFLOW] Research workflow completed successfully")
    
    return result


if __name__ == "__main__":
    # Check environment first
    check_environment()
    
    # Build and test the workflow
    workflow = build_research_workflow()
    
    # Visualize the workflow
    try:
        graph = workflow.get_graph()
        graph_png = graph.draw_mermaid_png()
        with open("workflow_graph.png", "wb") as f:
            f.write(graph_png)
        print("✅ LangGraph workflow visualization saved as: workflow_graph.png")
    except Exception as e:
        print(f"⚠️  Could not generate workflow graph: {e}")
    
    # Test with a sample query
    print("\n🧪 Testing workflow with sample query...")
    test_result = run_research_workflow("Machine Learning in Healthcare")
    print("✅ Workflow test completed!")