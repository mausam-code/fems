from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet, JobCategoryViewSet, CountryViewSet, SkillViewSet,
    VacancyViewSet, VacancyAttachmentViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'categories', JobCategoryViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'skills', SkillViewSet)
router.register(r'vacancies', VacancyViewSet)
router.register(r'attachments', VacancyAttachmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]