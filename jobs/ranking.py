from typing import List, Dict, Any
from .models import Job, JobApplication
from .nlp_matching import ResumeJobMatcher
from django.db.models import Q
import logging

# Set up logging
logger = logging.getLogger(__name__)

class CandidateRanker:
    def __init__(self):
        self.matcher = ResumeJobMatcher()

    def _calculate_experience_score(self, candidate_experience: float, required_experience: float) -> float:
        """
        Calculate experience match score (0-1)
        """
        if required_experience <= 0:
            return 1.0
        if candidate_experience >= required_experience:
            return 1.0
        return candidate_experience / required_experience

    def _calculate_education_score(self, candidate_education: str, required_education: str) -> float:
        """
        Calculate education match score (0-1)
        Simple education level hierarchy
        """
        education_levels = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5
        }
        
        candidate_level = 1  # Default to lowest level
        required_level = 1
        
        # Get education levels from the dictionary
        for level, score in education_levels.items():
            if level in (candidate_education or '').lower():
                candidate_level = score
            if level in (required_education or '').lower():
                required_level = score
                
        # Perfect or exceed match
        if candidate_level >= required_level:
            return 1.0
        
        # Partial match based on how close the levels are
        return candidate_level / required_level

    def _safe_calculate_similarity(self, resume_text: str, job_description: str) -> float:
        """
        Safely calculate similarity between resume and job description
        """
        if not resume_text or not job_description:
            logger.warning("Missing resume text or job description for similarity calculation")
            return 0.0
        try:
            return self.matcher.calculate_similarity(resume_text, job_description)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0

    def _safe_analyze_skills(self, resume_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> Dict:
        """
        Safely analyze skills match
        """
        try:
            return self.matcher.analyze_skill_match(resume_skills, required_skills, preferred_skills)
        except Exception as e:
            logger.error(f"Error analyzing skills: {str(e)}")
            return {'overall_score': 0, 'required_match': 0, 'preferred_match': 0, 'matched_skills': []}

    def rank_candidates(self, job: Job, applications=None) -> List[Dict[str, Any]]:
        """
        Rank candidates for a specific job based on multiple criteria
        """
        # Use provided applications or get all applications for this job
        if applications is None:
            applications = JobApplication.objects.filter(job=job)
        
        ranked_candidates = []
        
        for application in applications:
            try:
                resume = application.resume
                if not resume:
                    logger.warning(f"No resume found for application {application.id}")
                    continue

                # Get resume skills safely
                resume_skills = []
                if hasattr(resume, 'skills') and resume.skills:
                    if isinstance(resume.skills, str):
                        resume_skills = [s.strip() for s in resume.skills.split(',')]
                    elif isinstance(resume.skills, (list, tuple)):
                        resume_skills = resume.skills

                # Get job skills safely
                required_skills = []
                if job.required_skills:
                    if isinstance(job.required_skills, str):
                        required_skills = [s.strip() for s in job.required_skills.split(',')]
                    elif isinstance(job.required_skills, (list, tuple)):
                        required_skills = job.required_skills

                preferred_skills = []
                if job.preferred_skills:
                    if isinstance(job.preferred_skills, str):
                        preferred_skills = [s.strip() for s in job.preferred_skills.split(',')]
                    elif isinstance(job.preferred_skills, (list, tuple)):
                        preferred_skills = job.preferred_skills

                # Calculate main NLP similarity score
                content_similarity = self._safe_calculate_similarity(
                    getattr(resume, 'parsed_text', ''),
                    job.description or ''
                )
                
                # Calculate skills match
                skills_analysis = self._safe_analyze_skills(
                    resume_skills,
                    required_skills,
                    preferred_skills
                )
                
                # Calculate experience score
                experience_score = self._calculate_experience_score(
                    getattr(resume, 'years_of_experience', 0) or 0,
                    job.min_experience_years or 0
                )
                
                # Calculate education score
                education_score = self._calculate_education_score(
                    getattr(resume, 'education_level', ''),
                    job.education_level or ''
                )
                
                # Calculate weighted final score
                weights = {
                    'content_similarity': 0.4,
                    'skills_match': 0.3,
                    'experience': 0.2,
                    'education': 0.1
                }
                
                final_score = (
                    content_similarity * weights['content_similarity'] +
                    (skills_analysis['overall_score'] / 100) * weights['skills_match'] +
                    experience_score * weights['experience'] +
                    education_score * weights['education']
                ) * 100  # Convert to percentage
                
                ranked_candidates.append({
                    'application': application,
                    'candidate': application.candidate,
                    'resume': resume,
                    'content_similarity': content_similarity * 100,
                    'skills_match': {
                        'required_match_percentage': skills_analysis.get('required_match', 0),
                        'preferred_match_percentage': skills_analysis.get('preferred_match', 0),
                        'matched_skills': skills_analysis.get('matched_skills', [])
                    },
                    'experience_score': experience_score * 100,
                    'education_score': education_score * 100,
                    'final_score': final_score,
                    'matching_terms': self._safe_get_matching_terms(resume, job)
                })
            except Exception as e:
                logger.error(f"Error processing application {application.id}: {str(e)}")
                continue
        
        # Sort candidates by final score (descending)
        ranked_candidates.sort(key=lambda x: x['final_score'], reverse=True)
        return ranked_candidates

    def _safe_get_matching_terms(self, resume, job) -> List[str]:
        """
        Safely get matching terms between resume and job description
        """
        try:
            if not resume or not hasattr(resume, 'parsed_text') or not resume.parsed_text:
                return []
            return self.matcher.get_top_matching_terms(
                resume.parsed_text,
                job.description or '',
                top_n=5
            )
        except Exception as e:
            logger.error(f"Error getting matching terms: {str(e)}")
            return [] 