from django.contrib import admin
from django.utils.html import format_html
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_link', 'processing_status', 'uploaded_at', 'updated_at')
    list_filter = ('processing_status', 'uploaded_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'parsed_text')
    readonly_fields = ('uploaded_at', 'updated_at', 'parsed_text', 'extracted_skills',
                      'extracted_experience_years', 'extracted_education')
    ordering = ('-uploaded_at',)
    
    def file_link(self, obj):
        """Generate a link to download the resume file."""
        if obj.file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)
        return '-'
    file_link.short_description = 'Resume File'
