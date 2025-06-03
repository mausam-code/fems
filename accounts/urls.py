from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    # API Views
    RegisterView, LoginView, LogoutView, UserDetailView, ChangePasswordView,
    # Template Views
    LoginTemplateView, RegisterTemplateView, LogoutTemplateView, ProfileTemplateView, ChangePasswordTemplateView
)

app_name = 'accounts'

# API endpoints
api_urlpatterns = [
    path('register/', RegisterView.as_view(), name='api_register'),
    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
    path('profile/', UserDetailView.as_view(), name='api_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='api_change_password'),
]

# Template URLs
urlpatterns = [
    # Template views
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('register/', RegisterTemplateView.as_view(), name='register'),
    path('logout/', LogoutTemplateView.as_view(), name='logout'),
    path('profile/', ProfileTemplateView.as_view(), name='profile'),
    path('change-password/', ChangePasswordTemplateView.as_view(), name='change-password'),
    
    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/password-reset/done/'
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/password-reset-complete/'
    ), name='password_reset_confirm'),
    
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Include API endpoints
    *api_urlpatterns,
]