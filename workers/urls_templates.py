from django.urls import path
from .views_templates import (
    WorkerListView,
    WorkerDetailView,
    WorkerCreateView,
    WorkerUpdateView,
    WorkerProfileView,
    WorkerEducationCreateView,
    WorkerExperienceCreateView,
    WorkerSkillCreateView
)

app_name = 'workers'

urlpatterns = [
    path('', WorkerListView.as_view(), name='worker_list'),
    path('<uuid:pk>/', WorkerDetailView.as_view(), name='worker_detail'),
    path('create/', WorkerCreateView.as_view(), name='worker_create'),
    path('<uuid:pk>/update/', WorkerUpdateView.as_view(), name='worker_update'),
    path('profile/', WorkerProfileView.as_view(), name='worker_profile'),
    path('education/add/', WorkerEducationCreateView.as_view(), name='worker_education_add'),
    path('experience/add/', WorkerExperienceCreateView.as_view(), name='worker_experience_add'),
    path('skill/add/', WorkerSkillCreateView.as_view(), name='worker_skill_add'),
]