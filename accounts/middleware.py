from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class RoleBasedAccessMiddleware:
    """Middleware to handle role-based access control for templates."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define role-based URL patterns
        self.worker_urls = [
            '/applications/',
            '/vacancies/',
            '/documents/',
        ]
        
        self.employee_urls = [
            '/workers/',
            '/applications/',
            '/vacancies/',
            '/companies/',
        ]
        
        self.admin_urls = [
            '/workers/',
            '/employees/',
            '/applications/',
            '/vacancies/',
            '/companies/',
            '/countries/',
            '/documents/',
            '/services/',
        ]
        
        # URLs accessible to all authenticated users
        self.common_urls = [
            '/accounts/profile/',
            '/accounts/change-password/',
            '/dashboard/',
        ]
        
        # URLs accessible to unauthenticated users
        self.public_urls = [
            '/accounts/login/',
            '/accounts/register/',
            '/accounts/password_reset/',
            '/api/',
            '/admin/',
        ]
    
    def __call__(self, request):
        # Skip middleware for admin URLs
        if request.path.startswith('/admin/'):
            return self.get_response(request)
            
        # Skip middleware for API URLs
        if request.path.startswith('/api/'):
            return self.get_response(request)
            
        # Allow access to static and media files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
            
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Allow access to public URLs
            for url in self.public_urls:
                if request.path.startswith(url):
                    return self.get_response(request)
            
            # Redirect to login page for non-public URLs
            messages.warning(request, "Please log in to access this page.")
            return redirect(reverse('accounts:login'))
        
        # Allow access to common URLs for all authenticated users
        for url in self.common_urls:
            if request.path.startswith(url):
                return self.get_response(request)
        
        # Check user role and restrict access accordingly
        user_type = request.user.user_type
        
        if user_type == 'worker':
            allowed_urls = self.worker_urls + self.common_urls
            for url in allowed_urls:
                if request.path.startswith(url):
                    return self.get_response(request)
            
            # Redirect to dashboard if URL is not allowed
            messages.warning(request, "You don't have permission to access this page.")
            return redirect(reverse('dashboard'))
            
        elif user_type == 'employee':
            allowed_urls = self.employee_urls + self.common_urls
            for url in allowed_urls:
                if request.path.startswith(url):
                    return self.get_response(request)
            
            # Redirect to dashboard if URL is not allowed
            messages.warning(request, "You don't have permission to access this page.")
            return redirect(reverse('dashboard'))
            
        elif user_type == 'admin' or request.user.is_staff:
            # Admin users have access to all URLs
            return self.get_response(request)
        
        # Default response
        return self.get_response(request)