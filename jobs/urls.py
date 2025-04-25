from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Candidate views (public routes)
    path('', views.job_list, name='list'),  # Default job listing for candidates
    path('<int:pk>/', views.job_detail, name='detail'),  # Job details for everyone
    path('<int:pk>/apply/', views.apply_job, name='apply'),  # Apply for a job
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('my-applications/', views.my_applications, name='my_applications'),  # New URL pattern
    
    # Recruiter views (protected routes)
    path('recruiter/', views.recruiter_job_list, name='recruiter_list'),
    path('recruiter/create/', views.create_job, name='create'),
    path('recruiter/<int:pk>/edit/', views.edit_job, name='edit'),
    path('recruiter/<int:pk>/delete/', views.delete_job, name='delete'),
    path('recruiter/<int:pk>/publish/', views.publish_job, name='publish'),
    path('recruiter/<int:pk>/close/', views.close_job, name='close'),
    path('recruiter/<int:pk>/candidates/', views.JobCandidatesView.as_view(), name='candidates'),
    path('recruiter/<int:pk>/matches/', views.view_matches, name='matches'),
    path('applications/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
] 