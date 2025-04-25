from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

class Resume(models.Model):
    """Model for storing uploaded resumes and their parsed data."""
    
    class ProcessingStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        SUCCESS = 'SUCCESS', _('Success')
        FAILED = 'FAILED', _('Failed')
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume'
    )
    file = models.FileField(
        upload_to='resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
        verbose_name=_('Resume File')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Parsed data fields
    parsed_text = models.TextField(blank=True, null=True)
    extracted_skills = models.JSONField(default=list, blank=True)
    extracted_experience_years = models.PositiveIntegerField(null=True, blank=True)
    extracted_education = models.JSONField(default=list, blank=True)
    
    # Processing status
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING
    )
    processing_error = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('Resume')
        verbose_name_plural = _('Resumes')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Resume of {self.user.get_full_name() or self.user.username}"
    
    def get_file_extension(self):
        """Get the file extension of the uploaded resume."""
        name = self.file.name
        return name.split('.')[-1].lower() if '.' in name else ''
