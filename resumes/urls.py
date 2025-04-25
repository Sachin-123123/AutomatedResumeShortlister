from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('', views.resume_list, name='list'),
    path('upload/', views.upload_resume, name='upload'),
    path('<int:pk>/', views.resume_detail, name='detail'),
    path('<int:pk>/delete/', views.delete_resume, name='delete'),  # Single delete pattern with required pk
    path('parse-status/', views.parse_status, name='parse_status'),
    path('matches/', views.view_matches, name='matches'),
] 