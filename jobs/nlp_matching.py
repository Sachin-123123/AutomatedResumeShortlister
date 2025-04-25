from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple, Dict
import re

class ResumeJobMatcher:
    def __init__(self):
        """Initialize the TF-IDF vectorizer with custom parameters."""
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # Use both unigrams and bigrams
            max_features=5000,    # Limit vocabulary size
            strip_accents='unicode'
        )
        
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text data."""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def calculate_similarity(self, resume_text: str, job_description: str) -> float:
        """
        Calculate the similarity score between a resume and job description.
        
        Args:
            resume_text (str): The full text content of the resume
            job_description (str): The job description text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Preprocess texts
        resume_text = self.preprocess_text(resume_text)
        job_description = self.preprocess_text(job_description)
        
        # Create document corpus for TF-IDF
        documents = [resume_text, job_description]
        
        # Generate TF-IDF vectors
        try:
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity_score = cosine_similarity(
                tfidf_matrix[0:1],  # Resume vector
                tfidf_matrix[1:2]   # Job description vector
            )[0][0]
            
            return float(similarity_score)
            
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_top_matching_terms(self, resume_text: str, job_description: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get the top matching terms between resume and job description based on TF-IDF scores.
        
        Args:
            resume_text (str): The full text content of the resume
            job_description (str): The job description text
            top_n (int): Number of top terms to return
            
        Returns:
            List[Tuple[str, float]]: List of (term, score) tuples for top matching terms
        """
        # Preprocess texts
        resume_text = self.preprocess_text(resume_text)
        job_description = self.preprocess_text(job_description)
        
        # Create document corpus and generate TF-IDF vectors
        documents = [resume_text, job_description]
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        
        # Get feature names (terms)
        feature_names = np.array(self.vectorizer.get_feature_names_out())
        
        # Get TF-IDF scores for both documents
        resume_scores = tfidf_matrix[0].toarray()[0]
        job_scores = tfidf_matrix[1].toarray()[0]
        
        # Calculate term importance as the product of scores
        term_importance = resume_scores * job_scores
        
        # Get indices of top terms
        top_indices = term_importance.argsort()[-top_n:][::-1]
        
        # Return top terms and their scores
        return [(feature_names[i], float(term_importance[i])) for i in top_indices]

    def analyze_skill_match(self, resume_skills: List[str], job_required_skills: List[str], 
                          job_preferred_skills: List[str]) -> Dict[str, float]:
        """
        Analyze the match between resume skills and job skills.
        
        Args:
            resume_skills (List[str]): List of skills from the resume
            job_required_skills (List[str]): List of required skills for the job
            job_preferred_skills (List[str]): List of preferred skills for the job
            
        Returns:
            Dict[str, float]: Dictionary containing match percentages and scores
        """
        # Convert all skills to lowercase for comparison
        resume_skills = [skill.lower() for skill in resume_skills]
        required_skills = [skill.lower() for skill in job_required_skills]
        preferred_skills = [skill.lower() for skill in job_preferred_skills]
        
        # Calculate matches
        required_matches = sum(1 for skill in required_skills if skill in resume_skills)
        preferred_matches = sum(1 for skill in preferred_skills if skill in resume_skills)
        
        # Calculate percentages
        required_match_pct = (required_matches / len(required_skills)) if required_skills else 1.0
        preferred_match_pct = (preferred_matches / len(preferred_skills)) if preferred_skills else 1.0
        
        # Calculate overall score (weighing required skills more heavily)
        overall_score = (required_match_pct * 0.7) + (preferred_match_pct * 0.3)
        
        return {
            'required_match_percentage': required_match_pct * 100,
            'preferred_match_percentage': preferred_match_pct * 100,
            'overall_score': overall_score * 100,
            'required_matches': required_matches,
            'preferred_matches': preferred_matches,
            'total_required': len(required_skills),
            'total_preferred': len(preferred_skills)
        }

# Example usage:
def match_resume_to_job(resume_text: str, job_description: str, 
                       resume_skills: List[str], job_required_skills: List[str],
                       job_preferred_skills: List[str]) -> Dict[str, float]:
    """
    Main function to match a resume against a job posting.
    
    Args:
        resume_text (str): Full text content of the resume
        job_description (str): Full job description text
        resume_skills (List[str]): List of skills extracted from the resume
        job_required_skills (List[str]): List of required skills for the job
        job_preferred_skills (List[str]): List of preferred skills for the job
        
    Returns:
        Dict[str, float]: Dictionary containing various matching scores
    """
    matcher = ResumeJobMatcher()
    
    # Calculate overall content similarity
    content_similarity = matcher.calculate_similarity(resume_text, job_description)
    
    # Analyze skill matches
    skill_analysis = matcher.analyze_skill_match(
        resume_skills, 
        job_required_skills,
        job_preferred_skills
    )
    
    # Get top matching terms
    top_terms = matcher.get_top_matching_terms(resume_text, job_description)
    
    # Combine all results
    return {
        'content_similarity': content_similarity * 100,  # Convert to percentage
        'skill_match': skill_analysis,
        'top_matching_terms': top_terms
    } 