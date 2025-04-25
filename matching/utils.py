from typing import List, Dict, Set, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity_score(resume_text: str, job_description: str) -> float:
    """
    Calculate TF-IDF cosine similarity between resume text and job description.
    Returns a score between 0 and 100.
    """
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=5000,
        ngram_range=(1, 2)
    )
    
    # Fit and transform the texts
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Convert to percentage and ensure it's between 0 and 100
        return max(0, min(100, similarity * 100))
    except Exception:
        return 0.0

def calculate_skills_match_score(
    resume_skills: List[str],
    required_skills: List[str],
    preferred_skills: List[str] = None
) -> Tuple[float, List[str], List[str]]:
    """
    Calculate skills match score and identify matched/missing skills.
    Returns a tuple of (score, matched_skills, missing_skills).
    """
    if not required_skills:
        return 0.0, [], []
    
    # Convert to sets for easier comparison
    resume_skills_set = set(s.upper() for s in resume_skills)
    required_skills_set = set(s.upper() for s in required_skills)
    preferred_skills_set = set(s.upper() for s in (preferred_skills or []))
    
    # Calculate matches
    matched_required = resume_skills_set.intersection(required_skills_set)
    matched_preferred = resume_skills_set.intersection(preferred_skills_set)
    missing_required = required_skills_set - resume_skills_set
    
    # Calculate score
    required_score = len(matched_required) / len(required_skills_set) * 80
    preferred_score = (
        len(matched_preferred) / len(preferred_skills_set) * 20
        if preferred_skills_set else 0
    )
    
    total_score = required_score + preferred_score
    
    # Prepare return values
    matched_skills = sorted(list(matched_required.union(matched_preferred)))
    missing_skills = sorted(list(missing_required))
    
    return total_score, matched_skills, missing_skills

def calculate_experience_score(
    resume_years: int,
    required_years: int
) -> float:
    """
    Calculate experience match score.
    Returns a score between 0 and 100.
    """
    if resume_years is None:
        return 0.0
    
    if required_years == 0:
        return 100.0
    
    if resume_years >= required_years:
        return 100.0
    
    # Calculate percentage of required experience
    score = (resume_years / required_years) * 100
    return max(0, min(100, score))

def calculate_education_score(
    resume_education: List[Dict[str, str]],
    required_education: str
) -> float:
    """
    Calculate education match score.
    Returns a score between 0 and 100.
    """
    if not resume_education or not required_education:
        return 0.0
    
    # Education level weights
    education_levels = {
        'PHD': 4,
        'DOCTORATE': 4,
        'MASTER': 3,
        'BACHELOR': 2,
        'ASSOCIATE': 1
    }
    
    # Get highest education level from resume
    resume_level = 0
    for edu in resume_education:
        degree = edu['degree'].upper()
        for level, weight in education_levels.items():
            if level in degree:
                resume_level = max(resume_level, weight)
                break
    
    # Get required education level
    required_level = 0
    required_upper = required_education.upper()
    for level, weight in education_levels.items():
        if level in required_upper:
            required_level = weight
            break
    
    if required_level == 0:
        return 100.0
    
    if resume_level >= required_level:
        return 100.0
    
    # Calculate percentage based on levels
    score = (resume_level / required_level) * 100
    return max(0, min(100, score))

def calculate_match_scores(
    resume_text: str,
    resume_skills: List[str],
    resume_experience: int,
    resume_education: List[Dict[str, str]],
    job_description: str,
    required_skills: List[str],
    preferred_skills: List[str],
    required_experience: int,
    required_education: str
) -> Dict:
    """
    Calculate all match scores between a resume and a job.
    Returns a dictionary containing all scores and match details.
    """
    # Calculate individual scores
    similarity_score = calculate_similarity_score(resume_text, job_description)
    
    skills_score, matched_skills, missing_skills = calculate_skills_match_score(
        resume_skills,
        required_skills,
        preferred_skills
    )
    
    experience_score = calculate_experience_score(
        resume_experience,
        required_experience
    )
    
    education_score = calculate_education_score(
        resume_education,
        required_education
    )
    
    # Calculate weighted average
    weights = {
        'similarity': 0.4,
        'skills': 0.3,
        'experience': 0.2,
        'education': 0.1
    }
    
    overall_score = (
        similarity_score * weights['similarity'] +
        skills_score * weights['skills'] +
        experience_score * weights['experience'] +
        education_score * weights['education']
    )
    
    return {
        'similarity_score': similarity_score,
        'skills_match_score': skills_score,
        'experience_score': experience_score,
        'education_score': education_score,
        'overall_score': overall_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills
    } 