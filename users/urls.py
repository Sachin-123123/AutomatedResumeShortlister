from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('register/recruiter/', views.register_recruiter, name='register_recruiter'),
    path('register/candidate/', views.register_candidate, name='register_candidate'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
] 