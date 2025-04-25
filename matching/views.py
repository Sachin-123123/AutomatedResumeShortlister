from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from resumes.models import Resume
from jobs.models import Job
from .utils import calculate_match_scores

# Create your views here.

@login_required
def calculate_match(request, resume_id, job_id):
    """Calculate match score between a resume and a job."""
    resume = get_object_or_404(Resume, pk=resume_id)
    job = get_object_or_404(Job, pk=job_id)
    
    # Check permissions
    if resume.user != request.user and job.recruiter != request.user and not request.user.is_admin:
        return JsonResponse({
            'error': _('You do not have permission to view this match.')
        }, status=403)
    
    # Check if resume is processed
    if resume.processing_status != Resume.ProcessingStatus.SUCCESS:
        return JsonResponse({
            'error': _('Resume is still being processed. Please try again later.')
        }, status=400)
    
    # Calculate match scores
    match_scores = calculate_match_scores(
        resume_text=resume.parsed_text,
        resume_skills=resume.extracted_skills,
        resume_experience=resume.extracted_experience_years,
        resume_education=resume.extracted_education,
        job_description=job.description,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills,
        required_experience=job.min_experience_years,
        required_education=job.education_level
    )
    
    return JsonResponse(match_scores)

@login_required
def recalculate_all_matches(request, resume_id):
    """Recalculate matches for a resume against all active jobs."""
    resume = get_object_or_404(Resume, pk=resume_id)
    
    # Check permissions
    if resume.user != request.user and not request.user.is_admin:
        messages.error(request, _('You do not have permission to recalculate matches for this resume.'))
        return redirect('resumes:view')
    
    # Check if resume is processed
    if resume.processing_status != Resume.ProcessingStatus.SUCCESS:
        messages.warning(request, _('Resume is still being processed. Please try again later.'))
        return redirect('resumes:view')
    
    # Get all active jobs
    active_jobs = Job.objects.filter(status=Job.Status.PUBLISHED)
    
    # Calculate matches
    matches = []
    for job in active_jobs:
        match_scores = calculate_match_scores(
            resume_text=resume.parsed_text,
            resume_skills=resume.extracted_skills,
            resume_experience=resume.extracted_experience_years,
            resume_education=resume.extracted_education,
            job_description=job.description,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
            required_experience=job.min_experience_years,
            required_education=job.education_level
        )
        matches.append({
            'job': job,
            'scores': match_scores
        })
    
    # Sort matches by overall score
    matches.sort(key=lambda x: x['scores']['overall_score'], reverse=True)
    
    return render(request, 'matching/match_list.html', {
        'resume': resume,
        'matches': matches
    })

@login_required
def match_details(request, resume_id, job_id):
    """View detailed match information between a resume and a job."""
    resume = get_object_or_404(Resume, pk=resume_id)
    job = get_object_or_404(Job, pk=job_id)
    
    # Check permissions
    if resume.user != request.user and job.recruiter != request.user and not request.user.is_admin:
        messages.error(request, _('You do not have permission to view this match.'))
        return redirect('jobs:list')
    
    # Check if resume is processed
    if resume.processing_status != Resume.ProcessingStatus.SUCCESS:
        messages.warning(request, _('Resume is still being processed. Please try again later.'))
        return redirect('resumes:view')
    
    # Calculate match scores
    match_scores = calculate_match_scores(
        resume_text=resume.parsed_text,
        resume_skills=resume.extracted_skills,
        resume_experience=resume.extracted_experience_years,
        resume_education=resume.extracted_education,
        job_description=job.description,
        required_skills=job.required_skills,
        preferred_skills=job.preferred_skills,
        required_experience=job.min_experience_years,
        required_education=job.education_level
    )
    
    context = {
        'resume': resume,
        'job': job,
        'scores': match_scores
    }
    return render(request, 'matching/match_details.html', context)
