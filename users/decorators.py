from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

def role_required(allowed_roles):
    """
    Decorator for views that checks that the user has the required role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not isinstance(allowed_roles, (list, tuple)):
                roles = [allowed_roles]
            else:
                roles = allowed_roles
            
            # Convert string roles to uppercase before getting Role enum values
            roles = [role.upper() for role in roles]
            
            # Convert string roles to Role enum values
            enum_roles = [getattr(User.Role, role) for role in roles]
            
            if request.user.role not in enum_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorator for views that require admin access."""
    return role_required('ADMIN')(view_func)

def recruiter_required(view_func):
    """Decorator for views that require recruiter access."""
    return role_required('RECRUITER')(view_func)

def candidate_required(view_func):
    """Decorator for views that require candidate access."""
    return role_required('CANDIDATE')(view_func)

def recruiter_or_admin_required(view_func):
    """Decorator for views that require either recruiter or admin access."""
    return role_required(['RECRUITER', 'ADMIN'])(view_func) 