from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Employee, EmployeePermission
from .serializers import (
    EmployeeSerializer, EmployeeCreateSerializer, EmployeeUpdateSerializer,
    EmployeePermissionSerializer, EmployeePermissionUpdateSerializer
)

class IsAdminOrSelf(permissions.BasePermission):
    """Custom permission to only allow admins or the employee themselves to access their profile."""
    
    def has_object_permission(self, request, view, obj):
        # Allow admin users
        if request.user.is_staff:
            return True
        
        # Allow the employee to access their own profile
        if hasattr(request.user, 'employee_profile'):
            return obj.user == request.user
        
        return False

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Employee.objects.all()
        if hasattr(user, 'employee_profile'):
            if user.employee_profile.permissions.can_manage_employees:
                return Employee.objects.all()
            return Employee.objects.filter(user=user)
        return Employee.objects.none()
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        try:
            employee = Employee.objects.get(user=request.user)
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({"detail": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND)

class EmployeePermissionViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return EmployeePermission.objects.all()
        if hasattr(user, 'employee_profile'):
            if user.employee_profile.permissions.can_manage_employees:
                return EmployeePermission.objects.all()
            return EmployeePermission.objects.filter(employee__user=user)
        return EmployeePermission.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return EmployeePermissionUpdateSerializer
        return EmployeePermissionSerializer
    
    @action(detail=False, methods=['get'])
    def my_permissions(self, request):
        try:
            permissions = EmployeePermission.objects.get(employee__user=request.user)
            serializer = EmployeePermissionSerializer(permissions)
            return Response(serializer.data)
        except EmployeePermission.DoesNotExist:
            return Response({"detail": "Employee permissions not found"}, status=status.HTTP_404_NOT_FOUND)
