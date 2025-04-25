from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),  # Root path for home view
    path('recruiter/', views.recruiter_dashboard, name='recruiter'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('candidate/', views.candidate_dashboard, name='candidate'),
] 