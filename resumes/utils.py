import re
import spacy
import docx
import PyPDF2
from io import BytesIO
from typing import Dict, List, Tuple, Optional
from django.conf import settings

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Common technical skills and keywords
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go',
    # Web Technologies
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
    # Databases
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'elasticsearch',
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible',
    # Data Science & AI
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy',
    # Other Tools
    'git', 'jira', 'confluence', 'agile', 'scrum', 'rest api', 'graphql'
}

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text content from a DOCX file."""
    try:
        doc = docx.Document(BytesIO(file_bytes))
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")

def extract_skills(text: str) -> List[str]:
    """
    Extract skills from text using spaCy NER and pattern matching.
    Returns a list of unique skills.
    """
    # Process the text with spaCy
    doc = nlp(text.lower())
    
    # Extract skills using pattern matching
    skills = set()
    
    # Find technical skills
    for token in doc:
        if token.text in TECHNICAL_SKILLS:
            skills.add(token.text.upper())
    
    # Find multi-word technical skills
    for skill in TECHNICAL_SKILLS:
        if ' ' in skill and skill in text.lower():
            skills.add(skill.upper())
    
    # Find skills mentioned with keywords
    skill_patterns = [
        r'(?:proficient in|experience with|skilled in|knowledge of|expertise in)\s+([^,.]+)',
        r'(?:technologies|skills|tools)(?:\s+include)?:\s*([^.]+)',
        r'(?:programming languages|frameworks|platforms):\s*([^.]+)'
    ]
    
    for pattern in skill_patterns:
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            skill_text = match.group(1).strip()
            # Split by common separators and clean up
            for skill in re.split(r'[,;/&]', skill_text):
                skill = skill.strip()
                if skill in TECHNICAL_SKILLS:
                    skills.add(skill.upper())
    
    return sorted(list(skills))

def extract_experience(text: str) -> Optional[int]:
    """
    Extract years of experience from text.
    Returns the total years of experience or None if not found.
    """
    # Patterns to match experience
    patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience\s*(?:of|:)?\s*(\d+)\+?\s*years?',
        r'worked\s+(?:for\s+)?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s+(?:in\s+)?(?:the\s+)?(?:industry|field)',
        r'career\s+(?:spanning|of)\s+(\d+)\+?\s*years?'
    ]
    
    total_years = 0
    for pattern in patterns:
        matches = re.finditer(pattern, text.lower())
        for match in matches:
            years = int(match.group(1))
            total_years = max(total_years, years)
    
    return total_years if total_years > 0 else None

def extract_education(text: str) -> List[Dict[str, str]]:
    """
    Extract education information from text.
    Returns a list of dictionaries containing degree and field of study.
    """
    education = []
    
    # Common degree patterns
    degree_patterns = [
        # Doctoral
        r"(?:doctor|doctorate|ph\.?d\.?|d\.?phil\.?)\s+(?:degree\s+)?(?:of|in|)?\s+([^,\n]*)",
        # Master's
        r"(?:master'?s?|ms|ma|m\.s\.|m\.a\.|mba|m\.b\.a\.)\s+(?:degree\s+)?(?:of|in|)?\s+([^,\n]*)",
        # Bachelor's
        r"(?:bachelor'?s?|bs|ba|b\.s\.|b\.a\.)\s+(?:degree\s+)?(?:of|in|)?\s+([^,\n]*)",
        # Associate's
        r"(?:associate'?s?|aas|a\.a\.s\.)\s+(?:degree\s+)?(?:of|in|)?\s+([^,\n]*)"
    ]
    
    # Education keywords to help identify sections
    edu_keywords = r"education|qualification|degree|university|college|institute"
    
    # Find education section
    edu_sections = re.split(r'\n\s*(?:experience|work|employment|skills|projects)', text.lower())
    edu_text = ''
    for section in edu_sections:
        if re.search(edu_keywords, section.lower()):
            edu_text = section
            break
    
    # If no clear education section found, use the entire text
    if not edu_text:
        edu_text = text
    
    for pattern in degree_patterns:
        matches = re.finditer(pattern, edu_text.lower())
        for match in matches:
            field = match.group(1).strip()
            if field:
                degree_type = re.match(r"([^\s]+)", match.group(0)).group(1)
                education.append({
                    'degree': degree_type.upper(),
                    'field': field.title()
                })
    
    return education

def parse_resume(file_bytes: bytes, file_extension: str) -> Tuple[str, Dict]:
    """
    Parse a resume file and extract relevant information.
    Returns a tuple of (raw_text, parsed_data).
    """
    # Extract text based on file type
    if file_extension.lower() == 'pdf':
        text = extract_text_from_pdf(file_bytes)
    elif file_extension.lower() == 'docx':
        text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    # Parse the text
    parsed_data = {
        'skills': extract_skills(text),
        'experience_years': extract_experience(text),
        'education': extract_education(text)
    }
    
    return text, parsed_data 