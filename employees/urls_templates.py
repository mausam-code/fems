from django.urls import path
from .views_templates import (
    EmployeeListView,
    EmployeeDetailView,
    EmployeeCreateView,
    EmployeeUpdateView,
    EmployeeDashboardView,
    EmployeeApplicationsView,
    EmployeeWorkersView,
    EmployeeVacanciesView
)

app_name = 'employees'

urlpatterns = [
    path('', EmployeeListView.as_view(), name='employee_list'),
    path('<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('create/', EmployeeCreateView.as_view(), name='employee_create'),
    path('<int:pk>/update/', EmployeeUpdateView.as_view(), name='employee_update'),
    path('dashboard/', EmployeeDashboardView.as_view(), name='employee_dashboard'),
    path('applications/', EmployeeApplicationsView.as_view(), name='employee_applications'),
    path('workers/', EmployeeWorkersView.as_view(), name='employee_workers'),
    path('vacancies/', EmployeeVacanciesView.as_view(), name='employee_vacancies'),
]