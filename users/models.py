from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """Custom user model with role-based authentication."""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        RECRUITER = 'RECRUITER', _('Recruiter')
        CANDIDATE = 'CANDIDATE', _('Candidate')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDATE,
        verbose_name=_('Role')
    )
    
    # Additional fields for profile
    phone_number = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == self.Role.ADMIN or self.is_superuser
    
    def is_recruiter(self):
        """Check if user is a recruiter."""
        return self.role == self.Role.RECRUITER
    
    def is_candidate(self):
        """Check if user is a candidate."""
        return self.role == self.Role.CANDIDATE
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
