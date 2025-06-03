from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from accounts.views import DashboardView

# API Schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="FEMS API",
        default_version='v1',
        description="API for Foreign Employment Management System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# API URL patterns
api_urlpatterns = [
    path('accounts/', include('accounts.urls', namespace='api_accounts')),
    path('workers/', include('workers.urls')),
    path('employees/', include('employees.urls')),
    # path('applications/', include('applications.urls')),
    # path('vacancies/', include('vacancies.urls')),
    path('companies/', include('companies.urls')),
    path('countries/', include('countries.urls')),
    path('documents/', include('documents.urls')),
]

# Main URL patterns
urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Home page (redirects to login)
    path('', RedirectView.as_view(url='/accounts/register/'), name='home'),
    
    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # Template URLs
    path('accounts/', include('accounts.urls', namespace='accounts')),
    
    # Template URLs for each app
    path('workers/', include('workers.urls_templates', namespace='workers')),
    path('employees/', include('employees.urls_templates', namespace='employees')),
    path('applications/', include('applications.urls_templates', namespace='applications')),
    path('vacancies/', include('vacancies.urls_templates', namespace='vacancies')),
    path('documents/', include('documents.urls_templates', namespace='documents')),
    
    # API endpoints
    path('api/', include(api_urlpatterns)),
    
    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
