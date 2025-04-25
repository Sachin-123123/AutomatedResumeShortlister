from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.conf import settings
from users.decorators import role_required
from .forms import ResumeUploadForm
from .models import Resume
from .utils import parse_resume
from .tasks import process_resume_async
from django.core.paginator import Paginator

# Create your views here.

@login_required
@role_required('CANDIDATE')
def upload_resume(request):
    """Handle resume upload for candidates."""
    # Check if user already has a resume
    try:
        existing_resume = Resume.objects.get(user=request.user)
    except Resume.DoesNotExist:
        existing_resume = None
    
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=existing_resume)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.processing_status = Resume.ProcessingStatus.PROCESSING
            
            # Get the file extension
            file_extension = resume.get_file_extension()
            
            try:
                # Read the file content
                file_content = request.FILES['file'].read()
                
                # Parse the resume
                parsed_text, parsed_data = parse_resume(file_content, file_extension)
                
                # Update resume with parsed data
                resume.parsed_text = parsed_text
                resume.extracted_skills = parsed_data['skills']
                resume.extracted_experience_years = parsed_data['experience_years']
                resume.extracted_education = parsed_data['education']
                resume.processing_status = Resume.ProcessingStatus.SUCCESS
                
            except Exception as e:
                resume.processing_status = Resume.ProcessingStatus.FAILED
                resume.processing_error = str(e)
                messages.error(request, _('There was an error processing your resume. Please try again.'))
            
            resume.save()
            
            if resume.processing_status == Resume.ProcessingStatus.SUCCESS:
                messages.success(request, _('Your resume has been uploaded and processed successfully.'))
                # Trigger async task for additional processing if needed
                process_resume_async.delay(resume.id)
            
            return redirect('resumes:detail', pk=resume.pk)
    else:
        form = ResumeUploadForm(instance=existing_resume)
    
    context = {
        'form': form,
        'existing_resume': existing_resume,
        'max_size_mb': settings.MAX_RESUME_SIZE / (1024 * 1024)
    }
    return render(request, 'resumes/upload_resume.html', context)

@login_required
@role_required('CANDIDATE')
def view_resume(request):
    """View uploaded resume and its parsed information."""
    try:
        resume = Resume.objects.get(user=request.user)
        return render(request, 'resumes/view_resume.html', {'resume': resume})
    except Resume.DoesNotExist:
        messages.warning(request, _('You have not uploaded a resume yet.'))
        return redirect('resumes:upload')

@login_required
@role_required('CANDIDATE')
def delete_resume(request, pk):
    """Delete a resume."""
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    
    if request.method == 'POST':
        resume.delete()
        messages.success(request, _('Your resume has been deleted successfully.'))
        return redirect('resumes:list')
    
    return render(request, 'resumes/resume_confirm_delete.html', {
        'resume': resume
    })

@login_required
@role_required('CANDIDATE')
def parse_status(request):
    """Check the parsing status of the uploaded resume."""
    try:
        resume = Resume.objects.get(user=request.user)
        return JsonResponse({
            'status': resume.processing_status,
            'error': resume.processing_error or ''
        })
    except Resume.DoesNotExist:
        return JsonResponse({'error': 'No resume found'}, status=404)

@login_required
@role_required('CANDIDATE')
def view_matches(request):
    """View jobs that match the candidate's resume."""
    try:
        resume = Resume.objects.get(user=request.user)
        if resume.processing_status != Resume.ProcessingStatus.SUCCESS:
            messages.warning(request, _('Your resume is still being processed. Please check back later.'))
            return redirect('resumes:detail', pk=resume.pk)
        
        # Get matching jobs based on resume skills and experience
        from jobs.models import Job
        query = Job.objects.filter(status=Job.Status.PUBLISHED)
        
        # Add skill filter only if we have extracted skills
        if resume.extracted_skills:
            query = query.filter(required_skills__overlap=resume.extracted_skills)
        
        # Add experience filter only if we have extracted experience years
        if resume.extracted_experience_years is not None:
            query = query.filter(min_experience_years__lte=resume.extracted_experience_years)
        
        # Order by most recently published
        matching_jobs = query.order_by('-published_at')
        
        return render(request, 'resumes/matches.html', {
            'resume': resume,
            'matching_jobs': matching_jobs
        })
    except Resume.DoesNotExist:
        messages.warning(request, _('You need to upload a resume to view matching jobs.'))
        return redirect('resumes:upload')

@login_required
def resume_list(request):
    """Display list of user's resumes."""
    resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # Pagination
    paginator = Paginator(resumes, 10)  # Show 10 resumes per page
    page = request.GET.get('page')
    resumes = paginator.get_page(page)
    
    return render(request, 'resumes/resume_list.html', {
        'resumes': resumes
    })

@login_required
def resume_detail(request, pk):
    """Display resume details."""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check permissions:
    # 1. Resume owner can view their own resume
    # 2. Recruiters can view resumes of candidates who have applied to their jobs
    if request.user == resume.user:
        # Resume owner
        can_view = True
    elif request.user.is_recruiter or request.user.is_admin:
        # Check if this candidate has applied to any of the recruiter's jobs
        from jobs.models import JobApplication
        can_view = JobApplication.objects.filter(
            resume=resume,
            job__recruiter=request.user
        ).exists()
    else:
        can_view = False
    
    if not can_view:
        messages.error(request, _('You do not have permission to view this resume.'))
        return redirect('dashboard:home')
    
    return render(request, 'resumes/resume_detail.html', {
        'resume': resume
    })
