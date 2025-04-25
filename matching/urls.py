from django.urls import path
from . import views

app_name = 'matching'

urlpatterns = [
    path('calculate/<int:resume_id>/<int:job_id>/', views.calculate_match, name='calculate'),
    path('recalculate/<int:resume_id>/', views.recalculate_all_matches, name='recalculate_all'),
    path('details/<int:resume_id>/<int:job_id>/', views.match_details, name='details'),
] 