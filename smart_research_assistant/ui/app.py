# ui/app.py
import streamlit as st
import requests
import os

API_URL = "https://smart-research-backend.onrender.com/research" # FastAPI backend

st.set_page_config(page_title="Smart Research Assistant", page_icon="🔍", layout="centered")

st.title("🔍 Smart Research Assistant")
st.markdown("Enter your topic and generate a structured research summary using our multi-agent AI system.")

# Sidebar for information
with st.sidebar:
    st.header("About")
    st.markdown("""
    **Multi-Agent Workflow:**
    - 🔎 Search Agent
    - 📊 Analysis Agent  
    - ✅ Validator Agent
    - 📝 Summarizer Agent
    - 📄 Formatter Agent
    """)
    st.markdown("Built with **LangGraph** + **FastAPI** + **Streamlit**")

query = st.text_input("Enter your research topic:", placeholder="e.g., Machine Learning in Healthcare")

if st.button("Generate Research Report", type="primary"):
    if not query.strip():
        st.warning("Please enter a valid research topic.")
    else:
        with st.spinner("🔍 Processing your request through our multi-agent system..."):
            try:
                response = requests.post(API_URL, json={"topic_query": query})
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Research Completed Successfully!")
                    
                    # --- Validation Results ---
                    st.subheader("📊 Quality Assessment")
                    validation = result.get("validation_result", {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Sources", validation.get("source_count", 0))
                    with col2:
                        st.metric("Themes", validation.get("theme_count", 0))
                    with col3:
                        quality = validation.get("document_quality", "unknown")
                        st.metric("Quality", quality.title())
                    
                    # Show recommendations
                    recommendations = validation.get("recommendations", [])
                    if recommendations:
                        st.info("💡 **Recommendations:**")
                        for rec in recommendations:
                            st.write(f"- {rec}")
                    
                    # --- Summary Section ---
                    st.subheader("📝 Executive Summary")
                    st.write(result.get("final_summary", "No summary generated."))
                    
                    # --- Analysis Section ---
                    st.subheader("🔬 Analysis Results")
                    analysis = result.get("analysis_result", {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Key Themes:**")
                        for theme in analysis.get("themes", [])[:5]:
                            st.write(f"- {theme}")
                    
                    with col2:
                        st.write("**Top Keywords:**")
                        keywords = analysis.get("keywords", [])[:8]
                        keyword_text = ", ".join(keywords)
                        st.write(keyword_text)
                    
                    # --- Source Documents ---
                    st.subheader("📚 Source Documents")
                    docs = result.get("raw_documents", [])
                    for i, doc in enumerate(docs, 1):
                        with st.expander(f"Source {i}: {doc.get('title', 'Untitled')}"):
                            st.write(f"**Domain:** {doc.get('source_domain', 'Unknown')}")
                            if doc.get('url'):
                                st.write(f"**URL:** {doc['url']}")
                            st.write(f"**Snippet:** {doc.get('snippet', 'No content available')}")
                    
                    # --- Formatted Report ---
                    st.subheader("📄 Report Details")
                    formatted = result.get("formatted_report", {})
                    st.write(f"**Title:** {formatted.get('title', 'N/A')}")
                    st.write(f"**Validation Score:** {formatted.get('validation_score', 'N/A')}")
                    
                    # --- PDF Download Section ---
                    pdf_path = result.get("pdf_path", "")
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="📥 Download Full Research Report (PDF)",
                                data=pdf_file,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf"
                            )
                        st.success(f"PDF generated: {pdf_path}")
                    else:
                        st.info("PDF generation in progress or not available.")
                
                else:
                    st.error(f"❌ Failed to generate report. Server returned status: {response.status_code}")
                    st.write(f"Error details: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("🚫 Unable to connect to backend server!")
                st.info("Please make sure the FastAPI server is running on https://smart-research-backend.onrender.com/research")
                
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")

# Footer
st.markdown("---")
st.caption("Smart Research Assistant v1.0 | Powered by LangGraph Multi-Agent Framework")