from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApplicationViewSet, ApplicationDocumentViewSet
from .views_templates import (
    ApplicationListView, ApplicationDetailView, ApplicationCreateView, ApplicationUpdateView
)

# API router
router = DefaultRouter()
router.register(r'applications', ApplicationViewSet)
router.register(r'documents', ApplicationDocumentViewSet)

# API URLs
api_urlpatterns = [
    path('', include(router.urls)),
]

# Template URLs
urlpatterns = [
    # API endpoints
    path('api/', include(api_urlpatterns)),
    
    # Template views
    path('', ApplicationListView.as_view(), name='application_list'),
    path('<uuid:pk>/', ApplicationDetailView.as_view(), name='application_detail'),
    path('create/', ApplicationCreateView.as_view(), name='application_create'),
    path('<uuid:pk>/update/', ApplicationUpdateView.as_view(), name='application_update'),
    # path('<uuid:pk>/upload-document/', ApplicationDocumentUploadView.as_view(), name='application_upload_document'),
]