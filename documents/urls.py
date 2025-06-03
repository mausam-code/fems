from django.urls import path
from rest_framework.routers import DefaultRouter
from .views_templates import DocumentScannerView, ScannerResultsView, DocumentListView, DocumentDetailView

app_name = 'documents'

urlpatterns = [
    path('scanner/', DocumentScannerView.as_view(), name='scanner'),
    path('scanner/results/', ScannerResultsView.as_view(), name='scanner_results'),
    path('list/', DocumentListView.as_view(), name='document_list'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
]