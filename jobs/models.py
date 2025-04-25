from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Job(models.Model):
    """Model for storing job descriptions and requirements."""
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PUBLISHED = 'PUBLISHED', _('Published')
        CLOSED = 'CLOSED', _('Closed')
    
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs',
        limit_choices_to={'role': 'RECRUITER'}
    )
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    
    # Job requirements
    required_skills = models.JSONField(default=list)
    preferred_skills = models.JSONField(default=list, blank=True)
    min_experience_years = models.PositiveIntegerField(default=0)
    education_level = models.CharField(max_length=50, blank=True)
    
    # Job details
    job_type = models.CharField(max_length=50)
    salary_range = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def is_active(self):
        """Check if the job is currently active (published and not closed)."""
        return self.status == self.Status.PUBLISHED

class JobApplication(models.Model):
    """Model for storing job applications and their status."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Review')
        REVIEWING = 'REVIEWING', _('Under Review')
        SHORTLISTED = 'SHORTLISTED', _('Shortlisted')
        INTERVIEWED = 'INTERVIEWED', _('Interviewed')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')
        WITHDRAWN = 'WITHDRAWN', _('Withdrawn')
    
    # Relationships
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        limit_choices_to={'role': 'CANDIDATE'}
    )
    resume = models.ForeignKey(
        'resumes.Resume',
        on_delete=models.SET_NULL,
        null=True,
        related_name='applications'
    )
    
    # Application details
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    cover_letter = models.TextField(blank=True)
    matching_score = models.FloatField(default=0.0)
    recruiter_notes = models.TextField(blank=True)
    
    # Interview details
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_feedback = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Job Application')
        verbose_name_plural = _('Job Applications')
        ordering = ['-created_at']
        # Ensure a candidate can't apply to the same job multiple times
        unique_together = ['job', 'candidate']
    
    def __str__(self):
        return f"{self.candidate.get_full_name()} - {self.job.title}"
