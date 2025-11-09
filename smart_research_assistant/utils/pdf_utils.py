# utils/pdf_utils.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os
from datetime import datetime
from typing import List, Dict, Any
import re

def create_custom_styles():
    """Create clean, professional styles for the PDF."""
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'ResearchTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Heading 1 style - for main sections
    heading1_style = ParagraphStyle(
        'ResearchHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=12,
        spaceBefore=20,
        leftIndent=0,
        fontName='Helvetica-Bold'
    )
    
    # Heading 2 style - for sub-sections  
    heading2_style = ParagraphStyle(
        'ResearchHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=8,
        spaceBefore=15,
        leftIndent=0,
        fontName='Helvetica-Bold'
    )
    
    # Normal text style
    normal_style = ParagraphStyle(
        'ResearchNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Bullet style
    bullet_style = ParagraphStyle(
        'ResearchBullet',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        leftIndent=20,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    return {
        'title': title_style,
        'heading1': heading1_style,
        'heading2': heading2_style,
        'normal': normal_style,
        'bullet': bullet_style
    }

def clean_summary_text(summary: str) -> List[Dict[str, Any]]:
    """Clean and structure the summary into sections with proper formatting and numbering."""
    # First, completely remove all markdown headers from the entire text
    cleaned_summary = re.sub(r'#+\s*', '', summary)  # Remove ALL # headers
    
    sections = []
    current_section = {"title": "", "content": [], "original_title": ""}
    
    lines = cleaned_summary.split('\n')
    section_counter = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header (now without markdown)
        is_header = (
            re.match(r'^\d+\.\s+[A-Z]', line) or  # 1. Introduction
            re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*$', line) or  # Introduction
            any(keyword in line.lower() for keyword in [
                'introduction', 'methodology', 'approach', 'key insights', 
                'challenges', 'research gaps', 'real-world applications',
                'future scope', 'opportunities', 'conclusion', 'references',
                'summary', 'analysis', 'results', 'discussion', 'applications',
                'research summary'
            ])
        )
        
        if is_header and len(line) < 100:
            # Save previous section if exists
            if current_section["title"] or current_section["content"]:
                sections.append(current_section.copy())
            
            # Start new section with numbering
            section_counter += 1
            current_section = {
                "title": line, 
                "content": [], 
                "original_title": line,
                "number": section_counter
            }
        else:
            # Add content to current section
            if line:
                current_section["content"].append(line)
    
    # Add the last section
    if current_section["title"] or current_section["content"]:
        sections.append(current_section)
    
    return sections

def format_bullet_points(text: str) -> List[Paragraph]:
    """Format text with proper bullet points and handle different bullet types."""
    styles = create_custom_styles()
    paragraphs = []
    
    # Split by lines and process each
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Remove any remaining markdown from the line
        clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Remove bold
        clean_line = re.sub(r'\*(.*?)\*', r'\1', clean_line)  # Remove italic
        clean_line = re.sub(r'#+\s*', '', clean_line)  # Remove any remaining headers
        
        if not clean_line.strip():
            continue
            
        # Check for bullet points (•, *, -) or numbered lists
        if (clean_line.startswith(('•', '*', '-')) or 
            re.match(r'^\d+\.', clean_line) or
            re.match(r'^\*\s', clean_line)):
            
            # Clean the bullet point
            final_line = re.sub(r'^[•*\-]\s*', '', clean_line)  # Remove bullet chars
            final_line = re.sub(r'^\d+\.\s*', '', final_line)  # Remove numbers
            final_line = re.sub(r'^\*\s', '', final_line)  # Remove markdown bullets
            
            if final_line.strip():
                paragraphs.append(Paragraph(f"• {final_line.strip()}", styles['bullet']))
        else:
            # Regular paragraph
            if clean_line.strip():
                paragraphs.append(Paragraph(clean_line.strip(), styles['normal']))
    
    return paragraphs

def extract_bullet_content(text: str) -> List[str]:
    """Extract bullet point content from text."""
    bullets = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        # Clean the line first
        clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
        clean_line = re.sub(r'\*(.*?)\*', r'\1', clean_line)
        clean_line = re.sub(r'#+\s*', '', clean_line)
        
        if (clean_line.startswith(('•', '*', '-')) or 
            re.match(r'^\d+\.', clean_line) or
            re.match(r'^\*\s', clean_line)):
            
            # Clean the bullet point
            final_line = re.sub(r'^[•*\-]\s*', '', clean_line)
            final_line = re.sub(r'^\d+\.\s*', '', final_line)
            final_line = re.sub(r'^\*\s', '', final_line)
            
            if final_line.strip():
                bullets.append(final_line.strip())
    
    return bullets

def generate_pdf(topic: str, summary: str, analysis: Dict[str, Any], 
                 documents: List[Dict[str, Any]], validation: Dict[str, Any] = None) -> str:
    """Generate a clean, professional PDF research report with numbered headings and bullet points."""
    
    try:
        # Create outputs directory
        os.makedirs("outputs", exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic[:50]
        filename = f"outputs/Research_Report_{safe_topic}_{timestamp}.pdf"
        
        print(f"[PDF] Creating clean PDF: {filename}")
        
        # Create document
        pdf_doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Get styles
        styles = create_custom_styles()
        story = []
        
        # === COVER PAGE ===
        story.append(Paragraph("Research Report", styles['title']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(topic, styles['title']))
        story.append(Spacer(1, 40))
        
        date_str = f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}"
        story.append(Paragraph(date_str, styles['normal']))
        story.append(Paragraph("Smart Research Assistant - LangGraph Multi-Agent System", styles['normal']))
        
        story.append(PageBreak())
        
        # === QUALITY ASSESSMENT ===
        story.append(Paragraph("Research Quality Assessment", styles['heading1']))
        story.append(Spacer(1, 15))
        
        if validation:
            # Validation metrics
            metrics = [
                f"<b>Source Quality:</b> {validation.get('document_quality', 'Unknown')}",
                f"<b>Sources Analyzed:</b> {validation.get('source_count', 0)}",
                f"<b>Themes Identified:</b> {validation.get('theme_count', 0)}",
                f"<b>Sufficient Sources:</b> {'Yes' if validation.get('has_sufficient_sources') else 'No'}"
            ]
            
            for metric in metrics:
                story.append(Paragraph(metric, styles['normal']))
                story.append(Spacer(1, 5))
            
            story.append(Spacer(1, 10))
            story.append(Paragraph("Recommendations:", styles['heading2']))
            
            recommendations = validation.get('recommendations', [])
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", styles['bullet']))
        
        story.append(PageBreak())
        
        # === ANALYSIS RESULTS ===
        story.append(Paragraph("Analysis Results", styles['heading1']))
        story.append(Spacer(1, 15))
        
        if analysis:
            story.append(Paragraph("Key Themes Identified:", styles['heading2']))
            themes = analysis.get('themes', [])[:8]
            for theme in themes:
                story.append(Paragraph(f"• {theme}", styles['bullet']))
            
            story.append(Spacer(1, 15))
            story.append(Paragraph("Top Keywords:", styles['heading2']))
            keywords = analysis.get('keywords', [])[:12]
            keyword_text = ", ".join(keywords)
            story.append(Paragraph(keyword_text, styles['normal']))
        
        story.append(PageBreak())
        
        # === EXECUTIVE SUMMARY ===
        story.append(Paragraph("Executive Summary", styles['heading1']))
        story.append(Spacer(1, 15))
        
        # Process and structure the summary with numbering
        sections = clean_summary_text(summary)
        
        for section in sections:
            title = section.get("title", "").strip()
            content = section.get("content", [])
            section_number = section.get("number", 0)
            
            # Add section title with numbering if it exists
            if title:
                # Clean the title - remove any numbers and extra spaces
                clean_title = re.sub(r'^\d+\.\s*', '', title)  # Remove existing numbers
                clean_title = re.sub(r'\s+', ' ', clean_title).strip()  # Remove extra spaces
                
                # Skip if it's just "Research Summary" as it's redundant
                if "research summary" in clean_title.lower() and section_number == 1:
                    continue
                
                # Create numbered title
                if section_number > 0:
                    numbered_title = f"{section_number}. {clean_title}"
                else:
                    numbered_title = clean_title
                    
                story.append(Paragraph(numbered_title, styles['heading2']))
                story.append(Spacer(1, 8))
            
            # Add section content
            if content:
                # Combine content lines
                combined_content = " ".join(content)
                
                # Check if this section has bullet points
                bullets = extract_bullet_content(combined_content)
                
                if bullets:
                    # Format as bullet points
                    for bullet in bullets:
                        story.append(Paragraph(f"• {bullet}", styles['bullet']))
                        story.append(Spacer(1, 2))
                else:
                    # Format as regular paragraphs
                    paragraphs = format_bullet_points(combined_content)
                    for para in paragraphs:
                        story.append(para)
                        story.append(Spacer(1, 3))
            
            story.append(Spacer(1, 10))
        
        # === REFERENCE SOURCES ===
        if documents:
            story.append(PageBreak())
            story.append(Paragraph("Reference Sources", styles['heading1']))
            story.append(Spacer(1, 15))
            
            for i, doc in enumerate(documents, 1):
                title = doc.get('title', 'Untitled')
                domain = doc.get('source_domain', 'Unknown')
                snippet = doc.get('snippet', 'No content available')
                
                # Clean the snippet
                clean_snippet = re.sub(r'\*\*(.*?)\*\*', r'\1', snippet)
                clean_snippet = re.sub(r'\*(.*?)\*', r'\1', clean_snippet)
                clean_snippet = re.sub(r'#+\s*', '', clean_snippet)
                
                if len(clean_snippet) > 150:
                    clean_snippet = clean_snippet[:150] + '...'
                
                source_text = f"""
                <b>Source {i}: {title}</b><br/>
                <i>Domain: {domain}</i><br/>
                {clean_snippet}
                """
                
                story.append(Paragraph(source_text, styles['normal']))
                story.append(Spacer(1, 12))
        
        # Build the PDF
        pdf_doc.build(story)
        print(f"[PDF] Clean PDF generated successfully: {filename}")
        return filename
        
    except Exception as e:
        print(f"[PDF ERROR] Clean PDF generation failed: {e}")
        import traceback
        print(f"[PDF ERROR] Traceback: {traceback.format_exc()}")
        
        # Ultimate simple fallback
        return generate_simple_pdf(topic, summary)

def generate_simple_pdf(topic: str, summary: str) -> str:
    """Generate a very simple PDF as last resort."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"outputs/Research_Report_{safe_topic}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Simple clean content
        story.append(Paragraph(f"Research Report: {topic}", styles['Heading1']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 15))
        
        # Clean summary text (remove all markdown)
        clean_summary = re.sub(r'\*\*(.*?)\*\*', r'\1', summary)  # Remove bold
        clean_summary = re.sub(r'\*(.*?)\*', r'\1', clean_summary)  # Remove italic  
        clean_summary = re.sub(r'#+\s*', '', clean_summary)  # Remove headers
        
        paragraphs = clean_summary.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), styles['Normal']))
                story.append(Spacer(1, 10))
        
        doc.build(story)
        print(f"[PDF] Simple fallback PDF generated: {filename}")
        return filename
        
    except Exception as e:
        print(f"[PDF CRITICAL] All PDF methods failed: {e}")
        return ""