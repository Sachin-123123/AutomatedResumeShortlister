from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from django.db.models.functions import TruncMonth
from users.decorators import role_required
from jobs.models import Job, JobApplication
from resumes.models import Resume
from jobs.ranking import CandidateRanker
from django.contrib import messages

User = get_user_model()

@login_required
def home(request):
    """Home view that redirects users to their role-specific dashboard."""
    try:
        if request.user.is_admin():
            return redirect('dashboard:admin')
        elif request.user.is_recruiter():
            return redirect('dashboard:recruiter')
        else:  # is_candidate()
            return redirect('jobs:my_applications')
    except Exception as e:
        messages.error(request, 'Error determining user role. Please contact support.')
        return redirect('login')

@login_required
@role_required('recruiter')
def recruiter_dashboard(request):
    """Dashboard view for recruiters showing their jobs and top candidates."""
    # Get all jobs posted by this recruiter
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    
    # Initialize candidate ranker
    ranker = CandidateRanker()
    
    # Prepare data for each job
    jobs_data = []
    total_applications = 0  # Initialize counter for total applications
    
    for job in jobs:
        # Get ranked candidates for this job
        ranked_candidates = ranker.rank_candidates(job)[:5]  # Get top 5 candidates
        
        # Get applications count for this job
        job_applications = JobApplication.objects.filter(job=job).count()
        total_applications += job_applications  # Add to total
        
        jobs_data.append({
            'job': job,
            'top_candidates': ranked_candidates,
            'total_applications': job_applications
        })
    
    context = {
        'jobs_data': jobs_data,
        'total_active_jobs': Job.objects.filter(
            recruiter=request.user,
            status=Job.Status.PUBLISHED
        ).count(),
        'total_applications': total_applications  # Add to context
    }
    return render(request, 'dashboard/recruiter_dashboard.html', context)

@login_required
@role_required('admin')
def admin_dashboard(request):
    """Dashboard view for administrators showing platform analytics."""
    # Get basic counts
    total_users = User.objects.count()
    total_resumes = Resume.objects.count()
    total_jobs = Job.objects.count()
    total_applications = JobApplication.objects.count()
    
    # Get user role distribution
    role_distribution = User.objects.values('role').annotate(
        count=Count('id')
    ).order_by('role')
    
    # Get jobs created over time (last 6 months)
    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    jobs_over_time = Job.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Calculate application success rate
    applications_with_high_score = JobApplication.objects.filter(
        matching_score__gte=75
    ).count()
    application_success_rate = (
        (applications_with_high_score / total_applications * 100)
        if total_applications > 0 else 0
    )
    
    context = {
        'total_users': total_users,
        'total_resumes': total_resumes,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'role_distribution': list(role_distribution),
        'jobs_over_time': list(jobs_over_time),
        'application_success_rate': application_success_rate,
        'active_jobs': Job.objects.filter(status=Job.Status.PUBLISHED).count(),
        'recent_applications': JobApplication.objects.order_by('-created_at')[:5]
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
@role_required('candidate')
def candidate_dashboard(request):
    """Dashboard view for candidates showing their resume and application status."""
    # Get candidate's resume
    try:
        resume = Resume.objects.get(user=request.user)
        resume_exists = True
        parsed_skills = resume.extracted_skills if resume.extracted_skills else []
    except Resume.DoesNotExist:
        resume = None
        resume_exists = False
        parsed_skills = []
    
    # Get candidate's applications
    applications = JobApplication.objects.filter(
        candidate=request.user
    ).select_related('job').order_by('-created_at')
    
    # Calculate application statistics
    total_applications = applications.count()
    active_applications_count = applications.filter(
        status__in=['PENDING', 'REVIEWING', 'SHORTLISTED', 'INTERVIEWED']
    ).count()
    completed_applications_count = applications.filter(
        status__in=['ACCEPTED', 'REJECTED', 'WITHDRAWN']
    ).count()
    
    # Get matching job recommendations
    recommended_jobs = []
    if resume_exists:
        # Get active jobs and calculate matching scores
        active_jobs = Job.objects.filter(status=Job.Status.PUBLISHED)
        ranker = CandidateRanker()
        
        for job in active_jobs:
            match_score = ranker.matcher.calculate_similarity(
                resume.parsed_text,
                job.description
            ) * 100
            
            if match_score >= 60:  # Only show jobs with >60% match
                recommended_jobs.append({
                    'job': job,
                    'match_score': match_score
                })
        
        # Sort by match score and get top 5
        recommended_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        recommended_jobs = recommended_jobs[:5]
    
    context = {
        'resume': resume,
        'resume_exists': resume_exists,
        'parsed_skills': parsed_skills,
        'applications': applications,
        'total_applications': total_applications,
        'active_applications_count': active_applications_count,
        'completed_applications_count': completed_applications_count,
        'recommended_jobs': recommended_jobs
    }
    return render(request, 'dashboard/candidate_dashboard.html', context)
