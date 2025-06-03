from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Employee
from workers.models import Worker
from applications.models import Application
from vacancies.models import Vacancy
from .forms import EmployeeForm

class EmployeeAccessMixin(LoginRequiredMixin):
    """Mixin to ensure only employees or staff can access employee views"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Allow staff
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        
        # Check if user is an employee
        if hasattr(request.user, 'employee_profile'):
            # For detail/update views, ensure they can only access their own profile
            # unless they have employee management permission
            if hasattr(self, 'get_object'):
                obj = self.get_object()
                if obj.user == request.user or request.user.employee_profile.permissions.can_manage_employees:
                    return super().dispatch(request, *args, **kwargs)
            else:
                return super().dispatch(request, *args, **kwargs)
        
        # Redirect to dashboard if not authorized
        return redirect('dashboard')

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    
    def get_queryset(self):
        user = self.request.user
        # Only staff and employees with management permission can see all employees
        if user.is_staff:
            return Employee.objects.all()
        elif hasattr(user, 'employee_profile') and user.employee_profile.permissions.can_manage_employees:
            return Employee.objects.all()
        # Regular employees can only see their own profile
        elif hasattr(user, 'employee_profile'):
            return Employee.objects.filter(user=user)
        return Employee.objects.none()

class EmployeeDetailView(EmployeeAccessMixin, DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'

class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Only staff and employees with management permission can create employees
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.is_staff or (hasattr(request.user, 'employee_profile') and 
                                    request.user.employee_profile.permissions.can_manage_employees):
            return super().dispatch(request, *args, **kwargs)
        
        return redirect('dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EmployeeUpdateView(EmployeeAccessMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    
    def get_success_url(self):
        return reverse_lazy('employees:employee_detail', kwargs={'pk': self.object.pk})

class EmployeeDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'employees/employee_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'employee_profile'):
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.request.user.employee_profile
        
        # Get counts for dashboard stats based on permissions
        if employee.permissions.can_verify_applications:
            context['total_applications'] = Application.objects.count()
            context['pending_applications'] = Application.objects.filter(status='pending').count()
            context['approved_applications'] = Application.objects.filter(status='approved').count()
            context['rejected_applications'] = Application.objects.filter(status='rejected').count()
        
        if employee.permissions.can_verify_workers:
            context['total_workers'] = Worker.objects.count()
            context['verified_workers'] = Worker.objects.filter(is_verified=True).count()
            context['unverified_workers'] = Worker.objects.filter(is_verified=False).count()
        
        if employee.permissions.can_manage_vacancies:
            context['total_vacancies'] = Vacancy.objects.count()
            context['active_vacancies'] = Vacancy.objects.filter(is_active=True).count()
            context['inactive_vacancies'] = Vacancy.objects.filter(is_active=False).count()
        
        # Get recent items based on permissions
        if employee.permissions.can_verify_applications:
            context['recent_applications'] = Application.objects.order_by('-created_at')[:5]
        
        if employee.permissions.can_verify_workers:
            context['recent_workers'] = Worker.objects.order_by('-created_at')[:5]
        
        if employee.permissions.can_manage_vacancies:
            context['recent_vacancies'] = Vacancy.objects.order_by('-created_at')[:5]
        
        return context

class EmployeeApplicationsView(LoginRequiredMixin, ListView):
    template_name = 'employees/employee_applications.html'
    context_object_name = 'applications'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'employee_profile'):
            return redirect('dashboard')
        
        # Check if employee has permission to verify applications
        if not request.user.employee_profile.permissions.can_verify_applications:
            return redirect('employees:employee_dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Application.objects.all().order_by('-created_at')

class EmployeeWorkersView(LoginRequiredMixin, ListView):
    template_name = 'employees/employee_workers.html'
    context_object_name = 'workers'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'employee_profile'):
            return redirect('dashboard')
        
        # Check if employee has permission to verify workers
        if not request.user.employee_profile.permissions.can_verify_workers:
            return redirect('employees:employee_dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Worker.objects.all().order_by('-created_at')

class EmployeeVacanciesView(LoginRequiredMixin, ListView):
    template_name = 'employees/employee_vacancies.html'
    context_object_name = 'vacancies'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'employee_profile'):
            return redirect('dashboard')
        
        # Check if employee has permission to manage vacancies
        if not request.user.employee_profile.permissions.can_manage_vacancies:
            return redirect('employees:employee_dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Vacancy.objects.all().order_by('-created_at')