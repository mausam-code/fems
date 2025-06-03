from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, EmployeePermissionViewSet

router = DefaultRouter()
router.register(r'profiles', EmployeeViewSet)
router.register(r'permissions', EmployeePermissionViewSet, basename='employee-permission')

app_name = 'employees'

urlpatterns = [
    path('', include(router.urls)),
]