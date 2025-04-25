from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Resume
import filetype

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError(_('Please select a file to upload.'))
        
        # Check file size
        if file.size > settings.MAX_RESUME_SIZE:
            raise ValidationError(
                _('File size must not exceed %(max_size)s MB.'),
                params={'max_size': settings.MAX_RESUME_SIZE / (1024 * 1024)}
            )
        
        # Check file extension
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in ['pdf', 'docx']:
            raise ValidationError(
                _('Only PDF and DOCX files are allowed.')
            )
        
        # Read file content for MIME type detection
        file_content = file.read()
        # Reset file pointer to beginning
        file.seek(0)

        try:
            kind = filetype.guess(file_content)
            if kind is None:
                raise ValidationError('Could not determine file type. Please ensure you are uploading a valid PDF or DOCX file.')
            
            mime_type = kind.mime
            allowed_mime_types = [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            
            if mime_type not in allowed_mime_types:
                raise ValidationError(
                    f'Invalid file type. Detected MIME type: {mime_type}. '
                    'Only PDF and DOCX files are allowed.'
                )
        except Exception as e:
            raise ValidationError(
                'Could not verify file type. Please ensure you are uploading a valid PDF or DOCX file.'
            )
        
        return file 