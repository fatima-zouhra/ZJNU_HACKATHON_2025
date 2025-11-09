#========================================================#
# this script provides services to extract and query information from the ZJNU International Student Handbook PDF
# It loads the PDF, extracts text, and allows searching for relevant sections based on user questions.
#========================================================#


import os
import logging
from PyPDF2 import PdfReader
import re
import textwrap

logger = logging.getLogger(__name__)

# Handbook path - adjust based on your actual file location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HANDBOOK_PATH = os.path.join(BASE_DIR, "HandyChat", "static", "handbook", "zjnu_handbook_2025.pdf")

# Don't load immediately
handbook_text = None
handbook_loaded = False

def load_handbook_text():
    """Load handbook text only when needed"""
    global handbook_text, handbook_loaded
    
    if handbook_loaded and handbook_text:
        return handbook_text
        
    logger.info("Loading handbook PDF...")
    
    try:
        if not os.path.exists(HANDBOOK_PATH):
            logger.error(f"Handbook file not found at: {HANDBOOK_PATH}")
            handbook_text = ""
            handbook_loaded = True
            return handbook_text
            
        with open(HANDBOOK_PATH, "rb") as f:
            reader = PdfReader(f)
            text = ""
            total_pages = len(reader.pages)
            
            for page_num in range(total_pages):
                page_text = reader.pages[page_num].extract_text()
                text += page_text + "\n"
                logger.info(f"📄Page {page_num + 1}/{total_pages}: {len(page_text)} characters")
            
            handbook_text = text
            handbook_loaded = True
            logger.info(f"Successfully loaded handbook: {len(text)} total characters")
            return text
            
    except Exception as e:
        logger.error(f"Error loading handbook PDF: {e}")
        handbook_text = ""
        handbook_loaded = True
        return handbook_text

def clean_text(text):
    """Clean and format the extracted text"""
    if not text:
        return ""
    
    # Remove special characters and symbols
    text = re.sub(r'[•●◆■▲▼◇○◎§♠♥♦♣�]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()

def extract_english_sections(text):
    """Extract English content from the handbook"""
    if not text:
        return []
        
    paragraphs = text.split('\n')
    english_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if len(para) < 25:
            continue
            
        # Count English vs Chinese characters
        english_chars = len(re.findall(r'[a-zA-Z]', para))
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', para))
        total_chars = len(re.findall(r'[a-zA-Z\u4e00-\u9fff]', para))
        
        if total_chars > 0 and english_chars / total_chars > 0.5:
            clean_para = clean_text(para)
            if len(clean_para) > 40:
                english_paragraphs.append(clean_para)
    
    return english_paragraphs

def smart_search(question, handbook_content):
    """Find relevant content in PDF"""
    if not handbook_content:
        return []
        
    question_lower = question.lower()
    english_paragraphs = extract_english_sections(handbook_content)
    
    relevant_paragraphs = []
    
    for para in english_paragraphs:
        para_lower = para.lower()
        score = 0
        
        # Score based on keyword matches
        words = [word for word in question_lower.split() if len(word) > 3]
        score += sum(3 for word in words if word in para_lower)
        
        # Boost for structured content
        if re.search(r'\b(requirements|procedure|steps|policy|rule|must|should|shall|required)\b', para_lower):
            score += 3
        
        if score > 2:
            relevant_paragraphs.append((para, score))
    
    # Sort by relevance and remove duplicates
    relevant_paragraphs.sort(key=lambda x: x[1], reverse=True)
    
    unique_paragraphs = []
    seen_content = set()
    
    for para, score in relevant_paragraphs:
        # Simple deduplication
        signature = ' '.join(para.split()[:10])
        if signature not in seen_content and len(para) > 50:
            seen_content.add(signature)
            unique_paragraphs.append((para, score))
    
    return unique_paragraphs[:3]

def ask_handbook_clean(question):
    """Main function to query the PDF handbook"""
    logger.info(f"📖 PDF Handbook query: {question}")
    
    try:
        content = load_handbook_text()
        if not content or len(content) < 100:
            return "The handbook content is currently unavailable. Please try the simple handbook service or contact the International Student Office."
        
        relevant_content = smart_search(question, content)
        
        if relevant_content:
            # Build response from relevant content
            response = f"Regarding your question about '{question}':\n\n"
            response += "Based on the ZJNU International Student Handbook:\n\n"
            
            for i, (content, score) in enumerate(relevant_content, 1):
                # Clean and format the content
                content = re.sub(r'\s{2,}', ' ', content).strip()
                wrapped_content = textwrap.fill(content, width=80, break_long_words=False)
                response += f"{i}. {wrapped_content}\n\n"
            
            response += "For complete information, please refer to the official ZJNU International Student Handbook."
            logger.info(f"PDF handbook found {len(relevant_content)} relevant sections")
            return response
        else:
            return f"I couldn't find specific information about '{question}' in the PDF handbook. Please try rephrasing your question or contact the International Student Office."
            
    except Exception as e:
        logger.error(f"Error in PDF handbook service: {e}")
        return "I'm experiencing difficulties accessing the PDF handbook. Please try the simple handbook service or contact the International Student Office."

def get_handbook_status():
    """Get the current status of the PDF handbook"""
    try:
        content = load_handbook_text()
        english_paragraphs = extract_english_sections(content) if content else []
        
        return {
            "handbook_loaded": handbook_loaded,
            "has_content": bool(content and len(content) > 100),
            "content_length": len(content) if content else 0,
            "english_sections": len(english_paragraphs),
            "file_exists": os.path.exists(HANDBOOK_PATH),
            "file_path": HANDBOOK_PATH,
            "status": "available" if (content and len(content) > 100) else "unavailable"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }