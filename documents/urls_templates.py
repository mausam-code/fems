from django.urls import path
from . import views_templates

app_name = 'documents'

urlpatterns = [
    # Document scanner routes
    path('scanner/', views_templates.DocumentScannerView.as_view(), name='scanner'),
    path('scanner/results/', views_templates.ScannerResultsView.as_view(), name='scanner_results'),
    
    # Document management routes
    path('list/', views_templates.DocumentListView.as_view(), name='document_list'),
    path('detail/<int:pk>/', views_templates.DocumentDetailView.as_view(), name='document_detail'),
]