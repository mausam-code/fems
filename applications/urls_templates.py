from django.urls import path
from .views_templates import (
    ApplicationListView,
    ApplicationDetailView,
    ApplicationCreateView,
    ApplicationUpdateView,
    ApplicationStatusUpdateView,
    ApplicationDocumentListView,
    ApplicationDocumentCreateView,
    ApplicationDocumentVerifyView
)

app_name = 'applications'

urlpatterns = [
    path('', ApplicationListView.as_view(), name='application_list'),
    path('<uuid:pk>/', ApplicationDetailView.as_view(), name='application_detail'),
    path('create/', ApplicationCreateView.as_view(), name='application_create'),
    path('<uuid:pk>/update/', ApplicationUpdateView.as_view(), name='application_update'),
    path('<uuid:pk>/status/', ApplicationStatusUpdateView.as_view(), name='application_status_update'),
    path('<uuid:application_id>/documents/', ApplicationDocumentListView.as_view(), name='application_document_list'),
    path('<uuid:application_id>/documents/create/', ApplicationDocumentCreateView.as_view(), name='application_document_create'),
    path('documents/<int:pk>/verify/', ApplicationDocumentVerifyView.as_view(), name='application_document_verify'),
]