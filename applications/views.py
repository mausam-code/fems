from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import Application, ApplicationDocument, ApplicationNote, ApplicationStatusHistory
from .serializers import (
    ApplicationSerializer, ApplicationCreateSerializer, ApplicationUpdateSerializer,
    ApplicationStatusUpdateSerializer, ApplicationDocumentSerializer, ApplicationDocumentCreateSerializer,
    ApplicationDocumentVerifySerializer, ApplicationNoteSerializer, ApplicationNoteCreateSerializer,
    ApplicationStatusHistorySerializer
)

class IsWorkerOrEmployeePermission(permissions.BasePermission):
    """Custom permission to only allow workers to access their own applications and employees with proper permissions."""
    
    def has_object_permission(self, request, view, obj):
        # Allow admin users
        if request.user.is_staff:
            return True
        
        # Allow workers to access their own applications
        if hasattr(request.user, 'worker_profile'):
            return obj.worker.user == request.user
        
        # Allow employees with proper permissions
        if hasattr(request.user, 'employee_profile'):
            return request.user.employee_profile.permissions.can_verify_applications
        
        return False

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsWorkerOrEmployeePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'worker', 'vacancy', 'vacancy__company']
    search_fields = ['worker__user__first_name', 'worker__user__last_name', 'worker__user__email', 'vacancy__title']
    ordering_fields = ['application_date', 'last_updated', 'status']
    ordering = ['-application_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ApplicationUpdateSerializer
        elif self.action == 'update_status':
            return ApplicationStatusUpdateSerializer
        return ApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Application.objects.all()
        
        if hasattr(user, 'worker_profile'):
            return Application.objects.filter(worker__user=user)
        
        if hasattr(user, 'employee_profile'):
            if user.employee_profile.permissions.can_verify_applications:
                return Application.objects.all()
        
        return Application.objects.none()
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        application = self.get_object()
        serializer = self.get_serializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        application = self.get_object()
        documents = application.documents.all()
        serializer = ApplicationDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        application = self.get_object()
        serializer = ApplicationDocumentCreateSerializer(data=request.data, context={'application': application})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        application = self.get_object()
        
        # If the user is a worker, only return non-private notes
        if hasattr(request.user, 'worker_profile'):
            notes = application.notes.filter(is_private=False)
        else:
            notes = application.notes.all()
        
        serializer = ApplicationNoteSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        application = self.get_object()
        serializer = ApplicationNoteCreateSerializer(data=request.data, context={
            'request': request,
            'application': application
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        application = self.get_object()
        history = application.status_history.all()
        serializer = ApplicationStatusHistorySerializer(history, many=True)
        return Response(serializer.data)

class ApplicationDocumentViewSet(viewsets.ModelViewSet):
    queryset = ApplicationDocument.objects.all()
    serializer_class = ApplicationDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ApplicationDocument.objects.all()
        
        if hasattr(user, 'worker_profile'):
            return ApplicationDocument.objects.filter(application__worker__user=user)
        
        if hasattr(user, 'employee_profile'):
            if user.employee_profile.permissions.can_verify_applications:
                return ApplicationDocument.objects.all()
        
        return ApplicationDocument.objects.none()
    
    @action(detail=True, methods=['patch'])
    def verify(self, request, pk=None):
        document = self.get_object()
        serializer = ApplicationDocumentVerifySerializer(document, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
