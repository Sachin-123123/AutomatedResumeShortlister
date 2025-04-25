from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Job

class JobForm(forms.ModelForm):
    """Form for creating and editing jobs."""
    
    # Convert JSONField to more user-friendly form fields
    required_skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text=_('Enter each skill on a new line'),
    )
    preferred_skills = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text=_('Enter each skill on a new line'),
    )
    
    class Meta:
        model = Job
        fields = [
            'title',
            'company',
            'location',
            'description',
            'required_skills',
            'preferred_skills',
            'min_experience_years',
            'education_level',
            'job_type',
            'salary_range',
            'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert list to newline-separated string for initial display
        if self.instance.pk:
            self.initial['required_skills'] = '\n'.join(self.instance.required_skills)
            self.initial['preferred_skills'] = '\n'.join(self.instance.preferred_skills)
    
    def clean_required_skills(self):
        """Convert newline-separated skills to list."""
        skills = self.cleaned_data['required_skills']
        return [skill.strip() for skill in skills.split('\n') if skill.strip()]
    
    def clean_preferred_skills(self):
        """Convert newline-separated skills to list."""
        skills = self.cleaned_data['preferred_skills']
        return [skill.strip() for skill in skills.split('\n') if skill.strip()] 