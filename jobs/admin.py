from django.contrib import admin
from django.utils import timezone
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'status', 'created_at', 'is_active')
    list_filter = ('status', 'job_type', 'created_at')
    search_fields = ('title', 'company', 'description', 'required_skills')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('recruiter', 'title', 'company', 'location', 'description')
        }),
        ('Job Requirements', {
            'fields': ('required_skills', 'preferred_skills', 'min_experience_years', 'education_level')
        }),
        ('Job Details', {
            'fields': ('job_type', 'salary_range', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at', 'closed_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.recruiter = request.user
        if 'status' in form.changed_data:
            if obj.status == Job.Status.PUBLISHED:
                obj.published_at = timezone.now()
            elif obj.status == Job.Status.CLOSED:
                obj.closed_at = timezone.now()
        super().save_model(request, obj, form, change)
