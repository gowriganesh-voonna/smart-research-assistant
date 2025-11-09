# agents/summarizer_agent.py

import os
from typing import Dict, Any
from models.state_schema import ResearchState

# ✅ Use only LangChain-based Gemini model
from langchain_google_genai import ChatGoogleGenerativeAI

# 🔹 Enhanced academic summarizer prompt
SUMMARIZER_PROMPT = """
You are an **Expert Academic Research Assistant**. 
Your goal is to generate a clear, well-structured, and detailed **research summary** using the provided topic and reference materials.

You will receive:
- A **research topic** (main query)
- A collection of **reference documents or search results**

Follow this structure carefully and provide a professional, academic-style synthesis:

---

## 1. Introduction
Introduce the topic concisely. Explain its background, relevance, and why it is significant in today's research or industry landscape.

## 2. Methodology or Approach (if applicable)
Briefly discuss how current research or implementations approach this topic — mention algorithms, frameworks, or methodologies commonly used.

## 3. Key Insights
Summarize the major findings, advancements, and observed trends across the given documents.
Use complete sentences and explain concepts clearly — avoid bullet-only or shallow overviews.

## 4. Challenges / Research Gaps
Identify unresolved issues, limitations, or areas lacking exploration. Highlight where future research or innovation could contribute.

## 5. Real-World Applications
Provide examples or areas where this topic is applied in real-world scenarios, products, or industries.

## 6. Future Scope and Opportunities
Discuss potential future directions, open questions, or upcoming trends related to this topic.

## 7. Conclusion
Summarize the overall understanding of the topic. Emphasize its importance, impact, and what readers should take away.

## 8. References (if available)
List or summarize key papers, tools, or sources mentioned in the reference documents.

---

### Topic:
{topic}

### Reference Documents:
{docs_text}

Write in a **formal, academic tone**, maintaining paragraph structure and logical flow. Ensure clarity, coherence, and professional readability.
"""

def summarizer_agent(state: ResearchState) -> Dict[str, Any]:
    """Generate structured research summary using LangChain Gemini model."""
    topic = state.get("topic_query", "")
    docs = state.get("raw_documents", [])
    analysis = state.get("analysis_result", {})
    validation = state.get("validation_result", {})

    # Combine all reference document texts
    docs_text = "\n\n".join(
        [
            f"Title: {d.get('title', 'Untitled')}\nContent: {d.get('raw_content', d.get('snippet', ''))}"
            for d in docs
        ]
    )

    # Prepare prompt with validation insights
    prompt = SUMMARIZER_PROMPT.format(
        topic=topic,
        docs_text=docs_text + "\n\nPlease summarize concisely within 600-700 words with bullet points, include clear points and short paragraphs"
    )

    try:
        # 🚀 Initialize Gemini model via LangChain
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyDgIuCfgQnqE4l_J4EX-ClysACAw7cNq8s")
        )

        # ✅ Proper call to Gemini LLM
        response = llm.invoke(prompt)
        summary_text = response.content.strip()

        print(f"[SUMMARIZER] Generated summary with {len(summary_text)} characters")

    except Exception as e:
        print(f"[ERROR] Summarization failed: {e}")
        summary_text = (
            f"Topic: {topic}\nError generating structured summary. Please check your API configuration or input."
        )

    # ✅ Return only the summary - PDF generation moved to formatter_agent
    return {
        "final_summary": summary_text
        # No pdf_path here anymore
    }