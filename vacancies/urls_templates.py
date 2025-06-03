from django.urls import path
from .views_templates import (
    VacancyListView,
    VacancyDetailView,
    VacancyCreateView,
    VacancyUpdateView,
    VacancyDeleteView,
    CompanyListView,
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
    CountryListView,
    CountryDetailView
)

app_name = 'vacancies'

urlpatterns = [
    # Vacancy URLs
    path('', VacancyListView.as_view(), name='vacancy_list'),
    path('<int:pk>/', VacancyDetailView.as_view(), name='vacancy_detail'),
    path('create/', VacancyCreateView.as_view(), name='vacancy_create'),
    path('<int:pk>/update/', VacancyUpdateView.as_view(), name='vacancy_update'),
    path('<int:pk>/delete/', VacancyDeleteView.as_view(), name='vacancy_delete'),
    
    # Company URLs
    path('companies/', CompanyListView.as_view(), name='company_list'),
    path('companies/<int:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    path('companies/create/', CompanyCreateView.as_view(), name='company_create'),
    path('companies/<int:pk>/update/', CompanyUpdateView.as_view(), name='company_update'),
    
    # Country URLs
    path('countries/', CountryListView.as_view(), name='country_list'),
    path('countries/<int:pk>/', CountryDetailView.as_view(), name='country_detail'),
]