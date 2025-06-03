from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Worker, WorkerEducation, WorkerExperience, WorkerSkill
from .serializers import (
    WorkerSerializer, WorkerCreateSerializer, WorkerUpdateSerializer,
    WorkerEducationSerializer, WorkerExperienceSerializer, WorkerSkillSerializer
)

class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WorkerCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WorkerUpdateSerializer
        return WorkerSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.user_type == 'employee':
            return Worker.objects.all()
        return Worker.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        try:
            worker = Worker.objects.get(user=request.user)
            serializer = WorkerSerializer(worker)
            return Response(serializer.data)
        except Worker.DoesNotExist:
            return Response({"detail": "Worker profile not found"}, status=status.HTTP_404_NOT_FOUND)

class WorkerEducationViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerEducationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkerEducation.objects.filter(worker__user=self.request.user)
    
    def perform_create(self, serializer):
        worker = get_object_or_404(Worker, user=self.request.user)
        serializer.save(worker=worker)

class WorkerExperienceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkerExperience.objects.filter(worker__user=self.request.user)
    
    def perform_create(self, serializer):
        worker = get_object_or_404(Worker, user=self.request.user)
        serializer.save(worker=worker)

class WorkerSkillViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkerSkill.objects.filter(worker__user=self.request.user)
    
    def perform_create(self, serializer):
        worker = get_object_or_404(Worker, user=self.request.user)
        serializer.save(worker=worker)
