from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .models import Vacancy, Company, Country
from .forms import VacancyForm, CompanyForm

class EmployeePermissionMixin(LoginRequiredMixin):
    """Mixin to ensure only employees with proper permissions can access vacancy management views"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Allow staff
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        
        # Check if user is an employee with vacancy management permission
        if hasattr(request.user, 'employee_profile') and request.user.employee_profile.permissions.can_manage_vacancies:
            return super().dispatch(request, *args, **kwargs)
        
        # Redirect to dashboard if not authorized
        messages.error(request, "You don't have permission to manage vacancies.")
        return redirect('dashboard')

class VacancyListView(LoginRequiredMixin, ListView):
    model = Vacancy
    template_name = 'vacancies/vacancy_list.html'
    context_object_name = 'vacancies'
    
    def get_queryset(self):
        # All authenticated users can see vacancies, but we'll filter based on status
        queryset = Vacancy.objects.all()
        
        # For workers, only show active vacancies
        if self.request.user.user_type == 'worker':
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-created_at')

class VacancyDetailView(LoginRequiredMixin, DetailView):
    model = Vacancy
    template_name = 'vacancies/vacancy_detail.html'
    context_object_name = 'vacancy'

class VacancyCreateView(EmployeePermissionMixin, CreateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'vacancies/vacancy_form.html'
    success_url = reverse_lazy('vacancies:vacancy_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Vacancy created successfully.")
        return response

class VacancyUpdateView(EmployeePermissionMixin, UpdateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'vacancies/vacancy_form.html'
    
    def get_success_url(self):
        return reverse_lazy('vacancies:vacancy_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Vacancy updated successfully.")
        return response

class VacancyDeleteView(EmployeePermissionMixin, DeleteView):
    model = Vacancy
    template_name = 'vacancies/vacancy_confirm_delete.html'
    success_url = reverse_lazy('vacancies:vacancy_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Vacancy deleted successfully.")
        return super().delete(request, *args, **kwargs)

class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'vacancies/company_list.html'
    context_object_name = 'companies'
    
    def get_queryset(self):
        # Staff and employees with vacancy management permission can see all companies
        if self.request.user.is_staff or (hasattr(self.request.user, 'employee_profile') and 
                                        self.request.user.employee_profile.permissions.can_manage_vacancies):
            return Company.objects.all().order_by('name')
        
        # Workers can see companies with active vacancies
        if self.request.user.user_type == 'worker':
            companies_with_active_vacancies = Vacancy.objects.filter(is_active=True).values_list('company', flat=True)
            return Company.objects.filter(id__in=companies_with_active_vacancies).order_by('name')
        
        return Company.objects.none()

class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'vacancies/company_detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add vacancies for this company to context
        if self.request.user.user_type == 'worker':
            context['vacancies'] = Vacancy.objects.filter(company=self.object, is_active=True).order_by('-created_at')
        else:
            context['vacancies'] = Vacancy.objects.filter(company=self.object).order_by('-created_at')
        
        return context

class CompanyCreateView(EmployeePermissionMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'vacancies/company_form.html'
    success_url = reverse_lazy('vacancies:company_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Company created successfully.")
        return response

class CompanyUpdateView(EmployeePermissionMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'vacancies/company_form.html'
    
    def get_success_url(self):
        return reverse_lazy('vacancies:company_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Company updated successfully.")
        return response

class CountryListView(LoginRequiredMixin, ListView):
    model = Country
    template_name = 'vacancies/country_list.html'
    context_object_name = 'countries'
    
    def get_queryset(self):
        return Country.objects.all().order_by('name')

class CountryDetailView(LoginRequiredMixin, DetailView):
    model = Country
    template_name = 'vacancies/country_detail.html'
    context_object_name = 'country'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add companies and vacancies for this country to context
        context['companies'] = Company.objects.filter(country=self.object).order_by('name')
        
        if self.request.user.user_type == 'worker':
            context['vacancies'] = Vacancy.objects.filter(country=self.object, is_active=True).order_by('-created_at')
        else:
            context['vacancies'] = Vacancy.objects.filter(country=self.object).order_by('-created_at')
        
        return context