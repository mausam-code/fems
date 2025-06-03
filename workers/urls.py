from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkerViewSet, WorkerEducationViewSet, WorkerExperienceViewSet, WorkerSkillViewSet

router = DefaultRouter()
router.register(r'profiles', WorkerViewSet)
router.register(r'educations', WorkerEducationViewSet, basename='worker-education')
router.register(r'experiences', WorkerExperienceViewSet, basename='worker-experience')
router.register(r'skills', WorkerSkillViewSet, basename='worker-skill')

app_name = 'workers'

urlpatterns = [
    path('', include(router.urls)),
]