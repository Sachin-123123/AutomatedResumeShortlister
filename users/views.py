from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django import forms
from .forms import UserRegistrationForm, UserProfileForm
from .models import CustomUser
from .decorators import role_required

def register(request):
    """Generic registration view that redirects to role-specific registration."""
    return render(request, 'users/register_choice.html')

def register_user(request, default_role):
    """Common registration logic for both recruiters and candidates."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = default_role
            user.save()
            messages.success(request, _('Your account has been created! You can now log in.'))
            return redirect('login')
    else:
        form = UserRegistrationForm(initial={'role': default_role})
        form.fields['role'].widget = forms.HiddenInput()
    
    template_name = f'users/register_{default_role.lower()}.html'
    return render(request, template_name, {'form': form})

def register_recruiter(request):
    """Registration view for recruiters."""
    return register_user(request, CustomUser.Role.RECRUITER)

def register_candidate(request):
    """Registration view for candidates."""
    return register_user(request, CustomUser.Role.CANDIDATE)

@login_required
def profile(request):
    """View user profile."""
    return render(request, 'users/profile.html')

@login_required
def edit_profile(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})
