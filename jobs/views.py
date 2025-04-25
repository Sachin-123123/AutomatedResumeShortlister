from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from users.decorators import role_required, recruiter_or_admin_required
from .models import Job, JobApplication
from .forms import JobForm
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .ranking import CandidateRanker
from resumes.models import Resume
import json

@login_required
@recruiter_or_admin_required
def recruiter_job_list(request):
    """List jobs with filtering for recruiters/admins."""
    # Get jobs based on user role
    if request.user.is_admin:
        jobs = Job.objects.all()
    else:
        jobs = Job.objects.filter(recruiter=request.user)
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        jobs = jobs.filter(status=status)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(jobs.order_by('-created_at'), 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'jobs': jobs,
        'status_choices': Job.Status.choices,
        'selected_status': status,
        'search_query': search_query,
        'is_recruiter_view': True
    }
    return render(request, 'jobs/job_list.html', context)

@login_required
def job_list(request):
    """List published jobs for candidates."""
    # Get only published jobs
    jobs = Job.objects.filter(status=Job.Status.PUBLISHED)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(jobs.order_by('-published_at'), 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'jobs': jobs,
        'search_query': search_query,
        'is_recruiter_view': False
    }
    return render(request, 'jobs/job_list.html', context)

@login_required
def job_detail(request, pk):
    """View job details."""
    job = get_object_or_404(Job, pk=pk)
    
    # For candidates, only show published jobs
    if not (request.user.is_recruiter or request.user.is_admin):
        if job.status != Job.Status.PUBLISHED:
            messages.error(request, _('This job posting is not available.'))
            return redirect('jobs:list')
    # For recruiters, check if they own the job
    elif not request.user.is_admin and job.recruiter != request.user:
        messages.error(request, _('You do not have permission to view this job.'))
        return redirect('jobs:list')
    
    context = {
        'job': job,
        'is_recruiter': request.user.is_recruiter or request.user.is_admin,
        # Check if user has already applied
        'has_applied': JobApplication.objects.filter(
            job=job, 
            candidate=request.user
        ).exists() if not (request.user.is_recruiter or request.user.is_admin) else False
    }
    
    return render(request, 'jobs/job_detail.html', context)

@login_required
@recruiter_or_admin_required
def create_job(request):
    """Create a new job."""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, _('Job has been created successfully.'))
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm()
    
    return render(request, 'jobs/job_form.html', {
        'form': form,
        'title': _('Create Job'),
        'submit_text': _('Create')
    })

@login_required
@recruiter_or_admin_required
def edit_job(request, pk):
    """Edit an existing job."""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user has permission to edit this job
    if not request.user.is_admin and job.recruiter != request.user:
        messages.error(request, _('You do not have permission to edit this job.'))
        return redirect('jobs:list')
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, _('Job has been updated successfully.'))
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/job_form.html', {
        'form': form,
        'job': job,
        'title': _('Edit Job'),
        'submit_text': _('Update')
    })

@login_required
@recruiter_or_admin_required
def delete_job(request, pk):
    """Delete a job."""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user has permission to delete this job
    if not request.user.is_admin and job.recruiter != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': _('You do not have permission to delete this job.')
            }, status=403)
        messages.error(request, _('You do not have permission to delete this job.'))
        return redirect('jobs:list')
    
    if request.method == 'POST':
        job.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        messages.success(request, _('Job has been deleted successfully.'))
        return redirect('jobs:list')
    
    return render(request, 'jobs/job_confirm_delete.html', {'job': job})

@login_required
@recruiter_or_admin_required
def publish_job(request, pk):
    """Publish a job."""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user has permission to publish this job
    if not request.user.is_admin and job.recruiter != request.user:
        return JsonResponse({
            'error': _('You do not have permission to publish this job.')
        }, status=403)
    
    if request.method == 'POST':
        job.status = Job.Status.PUBLISHED
        job.published_at = timezone.now()
        job.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'error': _('Invalid request method.')}, status=400)

@login_required
@recruiter_or_admin_required
def close_job(request, pk):
    """Close a job."""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user has permission to close this job
    if not request.user.is_admin and job.recruiter != request.user:
        return JsonResponse({
            'error': _('You do not have permission to close this job.')
        }, status=403)
    
    if request.method == 'POST':
        job.status = Job.Status.CLOSED
        job.closed_at = timezone.now()
        job.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'error': _('Invalid request method.')}, status=400)

class JobCandidatesView(LoginRequiredMixin, DetailView):
    model = Job
    template_name = 'jobs/job_candidates.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the job object
        job = self.get_object()
        
        # Get all applications for this job
        applications = JobApplication.objects.filter(job=job)
        
        if applications.exists():
            # Create ranker instance and get ranked candidates
            ranker = CandidateRanker()
            ranked_candidates = ranker.rank_candidates(job, applications=applications)
            context['ranked_candidates'] = ranked_candidates
        else:
            context['ranked_candidates'] = []
            
        return context

@login_required
@recruiter_or_admin_required
def view_matches(request, pk):
    """View resumes that match the job requirements."""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user has permission to view matches for this job
    if not request.user.is_admin and job.recruiter != request.user:
        messages.error(request, _('You do not have permission to view matches for this job.'))
        return redirect('jobs:list')
    
    # Get all processed resumes
    processed_resumes = Resume.objects.filter(
        processing_status=Resume.ProcessingStatus.SUCCESS
    )
    
    # Filter resumes based on job requirements
    matching_resumes = []
    for resume in processed_resumes:
        # Check for matching skills
        required_skills = job.required_skills if job.required_skills else []
        preferred_skills = job.preferred_skills if job.preferred_skills else []
        resume_skills = resume.extracted_skills if resume.extracted_skills else []
        
        required_skills_match = any(skill in resume_skills for skill in required_skills)
        
        # Handle None values in experience comparison
        resume_experience = resume.extracted_experience_years or 0
        job_experience = job.min_experience_years or 0
        experience_match = resume_experience >= job_experience
        
        if required_skills_match and experience_match:
            # Calculate match score
            skill_match_count = sum(1 for skill in required_skills if skill in resume_skills)
            preferred_skill_match_count = sum(1 for skill in preferred_skills if skill in resume_skills)
            
            # Avoid division by zero
            required_skills_score = (skill_match_count / len(required_skills) * 0.6) if required_skills else 0.6
            preferred_skills_score = (preferred_skill_match_count / len(preferred_skills) * 0.2) if preferred_skills else 0.2
            
            # Calculate experience score (avoid division by zero)
            if job_experience > 0:
                experience_score = min(resume_experience / job_experience, 2) * 0.2
            else:
                experience_score = 0.2  # Give full score if no experience required
            
            match_score = (required_skills_score + preferred_skills_score + experience_score) * 100
            
            matching_resumes.append({
                'resume': resume,
                'match_score': round(match_score, 1),
                'matching_required_skills': [skill for skill in required_skills if skill in resume_skills],
                'matching_preferred_skills': [skill for skill in preferred_skills if skill in resume_skills]
            })
    
    # Sort matches by score (highest first)
    matching_resumes.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Pagination
    paginator = Paginator(matching_resumes, 10)  # 10 matches per page
    page = request.GET.get('page')
    matches = paginator.get_page(page)
    
    context = {
        'job': job,
        'matches': matches,
        'total_matches': len(matching_resumes)
    }
    return render(request, 'jobs/job_matches.html', context)

@login_required
def application_detail(request, pk):
    """View for displaying details of a specific job application."""
    application = get_object_or_404(JobApplication, pk=pk)
    
    # Ensure only the candidate who applied or the recruiter who posted the job can view
    if not (request.user == application.candidate or request.user == application.job.recruiter):
        messages.error(request, "You don't have permission to view this application.")
        return redirect('dashboard:home')
    
    # Calculate match scores if resume exists and has been processed
    if application.resume and application.resume.processing_status == Resume.ProcessingStatus.SUCCESS:
        try:
            job = application.job
            # Get skills from JSONField (they are already lists)
            required_skills = set(job.required_skills or [])
            preferred_skills = set(job.preferred_skills or [])
            resume_skills = set(application.resume.extracted_skills or [])
            
            # Calculate matching skills
            matching_required = required_skills.intersection(resume_skills)
            matching_preferred = preferred_skills.intersection(resume_skills)
            
            # Store matching and missing skills
            application.matching_required_skills = list(matching_required)
            application.missing_required_skills = list(required_skills - matching_required)
            application.matching_preferred_skills = list(matching_preferred)
            
            # Calculate individual scores
            if required_skills:
                application.required_skills_score = round((len(matching_required) / len(required_skills)) * 100)
            else:
                application.required_skills_score = 100  # If no required skills, give full score
            
            if preferred_skills:
                application.preferred_skills_score = round((len(matching_preferred) / len(preferred_skills)) * 100)
            else:
                application.preferred_skills_score = 100  # If no preferred skills, give full score
            
            # Experience score
            experience_years = application.resume.extracted_experience_years or 0
            required_years = job.min_experience_years or 0
            application.experience_years = experience_years
            if required_years > 0:
                application.experience_score = round(min(experience_years / required_years, 1) * 100)
            else:
                application.experience_score = 100  # If no experience required, give full score
            
            # Calculate weighted total score
            # Required skills: 60%, Preferred skills: 20%, Experience: 20%
            application.match_score = round(
                (application.required_skills_score * 0.6) +
                (application.preferred_skills_score * 0.2) +
                (application.experience_score * 0.2)
            )
            
            # Update the stored match score
            if application.matching_score != application.match_score:
                application.matching_score = application.match_score
                application.save(update_fields=['matching_score'])
        
        except Exception as e:
            print(f"Error calculating match score for application {application.pk}: {str(e)}")
    
    context = {
        'application': application,
        'job': application.job,
        'resume': application.resume,
        'is_recruiter': request.user == application.job.recruiter or request.user.is_admin
    }
    return render(request, 'jobs/application_detail.html', context)

@login_required
def apply_job(request, pk):
    """Handle job application submission."""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if job is still accepting applications
    if job.status != Job.Status.PUBLISHED:
        messages.error(request, _('This position is no longer accepting applications.'))
        return redirect('jobs:detail', pk=job.pk)
    
    # Check if user has already applied
    if JobApplication.objects.filter(job=job, candidate=request.user).exists():
        messages.warning(request, _('You have already applied for this position.'))
        return redirect('jobs:detail', pk=job.pk)
    
    # Get user's latest resume
    resume = Resume.objects.filter(
        user=request.user,
        processing_status=Resume.ProcessingStatus.SUCCESS
    ).order_by('-uploaded_at').first()
    
    if not resume:
        messages.error(request, _('Please upload and process your resume before applying.'))
        return redirect('resumes:upload')  # Redirect to resume upload page
    
    if request.method == 'POST':
        # Create job application
        application = JobApplication.objects.create(
            job=job,
            candidate=request.user,
            resume=resume,
            cover_letter=request.POST.get('cover_letter', '')
        )
        
        messages.success(request, _('Your application has been submitted successfully.'))
        return redirect('jobs:application_detail', pk=application.pk)
    
    return render(request, 'jobs/job_apply.html', {
        'job': job,
        'resume': resume
    })

@login_required
@role_required('CANDIDATE')
def my_applications(request):
    """Display a list of job applications for the current candidate."""
    applications = JobApplication.objects.filter(
        candidate=request.user
    ).select_related('job').order_by('-created_at')
    
    # Group applications by status
    status_groups = {
        'active': ['PENDING', 'REVIEWING', 'SHORTLISTED', 'INTERVIEWED'],
        'completed': ['ACCEPTED', 'REJECTED', 'WITHDRAWN']
    }
    
    grouped_applications = {
        'active': applications.filter(status__in=status_groups['active']),
        'completed': applications.filter(status__in=status_groups['completed'])
    }
    
    return render(request, 'jobs/my_applications.html', {
        'applications': applications,
        'grouped_applications': grouped_applications,
        'status_choices': JobApplication.Status.choices
    })

@login_required
@recruiter_or_admin_required
def view_applications(request, pk):
    """View all applications for a specific job."""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user has permission to view applications for this job
    if not request.user.is_admin and job.recruiter != request.user:
        messages.error(request, _('You do not have permission to view applications for this job.'))
        return redirect('jobs:list')
    
    # Get all applications for this job with related data
    applications = JobApplication.objects.filter(job=job)\
        .select_related('candidate', 'resume')\
        .order_by('-created_at')
    
    # Calculate match scores for each application
    for application in applications:
        # Initialize default values
        application.match_score = 0
        application.required_skills_score = 0
        application.preferred_skills_score = 0
        application.experience_score = 0
        application.matching_required_skills = []
        application.missing_required_skills = []
        application.matching_preferred_skills = []
        application.experience_years = 0
        
        # Only calculate scores if resume exists and has been processed
        if application.resume and application.resume.processing_status == Resume.ProcessingStatus.SUCCESS:
            try:
                # Get skills from JSONField (they are already lists)
                required_skills = set(job.required_skills or [])
                preferred_skills = set(job.preferred_skills or [])
                resume_skills = set(application.resume.extracted_skills or [])
                
                # Calculate matching skills
                matching_required = required_skills.intersection(resume_skills)
                matching_preferred = preferred_skills.intersection(resume_skills)
                
                # Store matching and missing skills for display
                application.matching_required_skills = list(matching_required)
                application.missing_required_skills = list(required_skills - matching_required)
                application.matching_preferred_skills = list(matching_preferred)
                
                # Calculate individual scores
                if required_skills:
                    application.required_skills_score = round((len(matching_required) / len(required_skills)) * 100)
                else:
                    application.required_skills_score = 100  # If no required skills, give full score
                
                if preferred_skills:
                    application.preferred_skills_score = round((len(matching_preferred) / len(preferred_skills)) * 100)
                else:
                    application.preferred_skills_score = 100  # If no preferred skills, give full score
                
                # Experience score
                experience_years = application.resume.extracted_experience_years or 0
                required_years = job.min_experience_years or 0
                application.experience_years = experience_years
                if required_years > 0:
                    application.experience_score = round(min(experience_years / required_years, 1) * 100)
                else:
                    application.experience_score = 100  # If no experience required, give full score
                
                # Calculate weighted total score
                # Required skills: 60%, Preferred skills: 20%, Experience: 20%
                application.match_score = round(
                    (application.required_skills_score * 0.6) +
                    (application.preferred_skills_score * 0.2) +
                    (application.experience_score * 0.2)
                )
                
                # Update the stored match score
                if application.matching_score != application.match_score:
                    application.matching_score = application.match_score
                    application.save(update_fields=['matching_score'])
            
            except Exception as e:
                print(f"Error calculating match score for application {application.pk}: {str(e)}")
                # Keep default values in case of error
        
    # Add shortlisted count to the queryset
    applications.shortlisted = applications.filter(status='SHORTLISTED')
    
    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'jobs/job_applications.html', context)

@login_required
@recruiter_or_admin_required
def update_application_status(request, pk):
    """Update the status of a job application."""
    application = get_object_or_404(JobApplication, pk=pk)
    
    # Check if user has permission to update this application
    if not request.user.is_admin and application.job.recruiter != request.user:
        return JsonResponse({
            'error': _('You do not have permission to update this application.')
        }, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if new_status not in dict(JobApplication.Status.choices):
                return JsonResponse({
                    'error': _('Invalid status provided.')
                }, status=400)
            
            application.status = new_status
            application.save()
            
            return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': _('Invalid JSON data provided.')
            }, status=400)
    
    return JsonResponse({'error': _('Invalid request method.')}, status=405)
