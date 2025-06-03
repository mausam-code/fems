from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Company, JobCategory, Country, Skill, Vacancy, VacancyAttachment
from .serializers import (
    CompanySerializer, JobCategorySerializer, CountrySerializer, SkillSerializer,
    VacancyListSerializer, VacancyDetailSerializer, VacancyCreateSerializer, VacancyUpdateSerializer,
    VacancyAttachmentSerializer, VacancyAttachmentCreateSerializer
)

class IsEmployeeWithPermission(permissions.BasePermission):
    """Custom permission to only allow employees with proper permissions."""
    
    def has_permission(self, request, view):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Allow admin users
        if request.user.is_staff:
            return True
        
        # Allow employees with proper permissions
        if hasattr(request.user, 'employee_profile'):
            return request.user.employee_profile.permissions.can_manage_vacancies
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Allow read-only access for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Allow admin users
        if request.user.is_staff:
            return True
        
        # Allow employees with proper permissions
        if hasattr(request.user, 'employee_profile'):
            return request.user.employee_profile.permissions.can_manage_vacancies
        
        return False

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsEmployeeWithPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'contact_email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [IsEmployeeWithPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsEmployeeWithPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name']
    ordering = ['name']

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsEmployeeWithPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'company', 'category', 'country', 'employment_type', 'is_featured']
    search_fields = ['title', 'description', 'requirements', 'responsibilities', 'company__name', 'location']
    ordering_fields = ['posted_date', 'application_deadline', 'title', 'company__name']
    ordering = ['-is_featured', '-posted_date']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_attachment']:
            return [IsEmployeeWithPermission()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VacancyListSerializer
        elif self.action == 'create':
            return VacancyCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VacancyUpdateSerializer
        elif self.action == 'add_attachment':
            return VacancyAttachmentCreateSerializer
        return VacancyDetailSerializer
    
    def get_queryset(self):
        queryset = Vacancy.objects.all()
        
        # Filter by open status if requested
        open_only = self.request.query_params.get('open_only', None)
        if open_only and open_only.lower() == 'true':
            queryset = queryset.filter(
                status='open',
                application_deadline__gte=timezone.now().date()
            )
        
        # Filter by skills if requested
        skills = self.request.query_params.get('skills', None)
        if skills:
            skill_ids = [int(s) for s in skills.split(',') if s.isdigit()]
            if skill_ids:
                queryset = queryset.filter(skills_required__id__in=skill_ids).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def attachments(self, request, pk=None):
        vacancy = self.get_object()
        attachments = vacancy.attachments.all()
        serializer = VacancyAttachmentSerializer(attachments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        vacancy = self.get_object()
        serializer = self.get_serializer(data=request.data, context={
            'request': request,
            'vacancy': vacancy
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class VacancyAttachmentViewSet(viewsets.ModelViewSet):
    queryset = VacancyAttachment.objects.all()
    serializer_class = VacancyAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsEmployeeWithPermission()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
