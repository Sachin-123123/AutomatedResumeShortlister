from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class MatchScore(models.Model):
    """Model for storing the matching scores between resumes and jobs."""
    
    resume = models.ForeignKey(
        'resumes.Resume',
        on_delete=models.CASCADE,
        related_name='match_scores'
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='match_scores'
    )
    
    # Scores (0-100)
    similarity_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('TF-IDF cosine similarity score')
    )
    skills_match_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Percentage of required skills matched')
    )
    experience_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Score based on years of experience match')
    )
    education_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Score based on education level match'),
        null=True,
        blank=True
    )
    
    # Overall weighted score
    overall_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Weighted average of all scores')
    )
    
    # Match details
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    
    # Timestamps
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Match Score')
        verbose_name_plural = _('Match Scores')
        ordering = ['-overall_score']
        constraints = [
            models.UniqueConstraint(
                fields=['resume', 'job'],
                name='unique_resume_job_match'
            )
        ]
    
    def __str__(self):
        return f"Match: {self.resume.user.get_full_name()} - {self.job.title} ({self.overall_score:.2f}%)"
    
    def calculate_overall_score(self):
        """Calculate the weighted average of all scores."""
        weights = {
            'similarity': 0.4,
            'skills': 0.3,
            'experience': 0.2,
            'education': 0.1
        }
        
        scores = {
            'similarity': self.similarity_score,
            'skills': self.skills_match_score,
            'experience': self.experience_score,
            'education': self.education_score or 0
        }
        
        self.overall_score = sum(
            score * weights[category]
            for category, score in scores.items()
        )
        return self.overall_score
