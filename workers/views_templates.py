from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Worker, WorkerEducation, WorkerExperience, WorkerSkill
from .forms import WorkerForm, WorkerEducationForm, WorkerExperienceForm, WorkerSkillForm

class WorkerAccessMixin(LoginRequiredMixin):
    """Mixin to ensure proper access control for worker views"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Allow staff
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        
        # Check if user is an employee with worker management permission
        if hasattr(request.user, 'employee_profile') and request.user.employee_profile.permissions.can_manage_workers:
            return super().dispatch(request, *args, **kwargs)
        
        # For workers, check if they own the profile
        if request.user.user_type == 'worker' and hasattr(self, 'get_object'):
            obj = self.get_object()
            if obj.user == request.user:
                return super().dispatch(request, *args, **kwargs)
        
        # For list views, the queryset will be filtered in get_queryset
        if not hasattr(self, 'get_object'):
            return super().dispatch(request, *args, **kwargs)
        
        # Redirect to dashboard if not authorized
        return redirect('dashboard')

class WorkerListView(WorkerAccessMixin, ListView):
    model = Worker
    template_name = 'workers/worker_list.html'
    context_object_name = 'workers'
    
    def get_queryset(self):
        user = self.request.user
        
        # Staff and employees with worker management permission can see all workers
        if user.is_staff or (hasattr(user, 'employee_profile') and 
                           user.employee_profile.permissions.can_manage_workers):
            return Worker.objects.all().order_by('-created_at')
        
        # Workers can only see their own profile
        if user.user_type == 'worker':
            return Worker.objects.filter(user=user)
        
        return Worker.objects.none()

class WorkerDetailView(WorkerAccessMixin, DetailView):
    model = Worker
    template_name = 'workers/worker_detail.html'
    context_object_name = 'worker'

class WorkerCreateView(WorkerAccessMixin, CreateView):
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'
    success_url = reverse_lazy('workers:worker_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Worker profile created successfully')
        return super().form_valid(form)

class WorkerUpdateView(WorkerAccessMixin, UpdateView):
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'
    
    def get_success_url(self):
        return reverse_lazy('workers:worker_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Worker profile updated successfully')
        return super().form_valid(form)

class WorkerProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'workers/worker_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            worker = Worker.objects.get(user=self.request.user)
            context['worker'] = worker
            context['educations'] = worker.educations.all()
            context['experiences'] = worker.experiences.all()
            context['skills'] = worker.skills.all()
        except Worker.DoesNotExist:
            context['worker'] = None
        return context

class WorkerEducationCreateView(LoginRequiredMixin, CreateView):
    model = WorkerEducation
    form_class = WorkerEducationForm
    template_name = 'workers/education_form.html'
    success_url = reverse_lazy('workers:worker_profile')
    
    def form_valid(self, form):
        worker = get_object_or_404(Worker, user=self.request.user)
        form.instance.worker = worker
        messages.success(self.request, 'Education added successfully')
        return super().form_valid(form)

class WorkerExperienceCreateView(LoginRequiredMixin, CreateView):
    model = WorkerExperience
    form_class = WorkerExperienceForm
    template_name = 'workers/experience_form.html'
    success_url = reverse_lazy('workers:worker_profile')
    
    def form_valid(self, form):
        worker = get_object_or_404(Worker, user=self.request.user)
        form.instance.worker = worker
        messages.success(self.request, 'Experience added successfully')
        return super().form_valid(form)

class WorkerSkillCreateView(LoginRequiredMixin, CreateView):
    model = WorkerSkill
    form_class = WorkerSkillForm
    template_name = 'workers/skill_form.html'
    success_url = reverse_lazy('workers:worker_profile')
    
    def form_valid(self, form):
        worker = get_object_or_404(Worker, user=self.request.user)
        form.instance.worker = worker
        messages.success(self.request, 'Skill added successfully')
        return super().form_valid(form)

class WorkerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'workers/worker_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'worker':
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = Worker.objects.get(user=self.request.user)
        
        # Get worker's applications
        applications = Application.objects.filter(worker=worker)
        
        # Get counts for dashboard stats
        context['total_applications'] = applications.count()
        context['pending_applications'] = applications.filter(status='pending').count()
        context['approved_applications'] = applications.filter(status='approved').count()
        context['rejected_applications'] = applications.filter(status='rejected').count()
        
        # Get recent applications
        context['recent_applications'] = applications.order_by('-created_at')[:5]
        
        return context

class WorkerApplicationsView(LoginRequiredMixin, ListView):
    template_name = 'workers/worker_applications.html'
    context_object_name = 'applications'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'worker':
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        try:
            worker = Worker.objects.get(user=self.request.user)
            return Application.objects.filter(worker=worker).order_by('-created_at')
        except Worker.DoesNotExist:
            return Application.objects.none()

class WorkerDocumentsView(LoginRequiredMixin, ListView):
    template_name = 'workers/worker_documents.html'
    context_object_name = 'documents'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'worker':
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        try:
            worker = Worker.objects.get(user=self.request.user)
            # Get documents from all worker's applications
            applications = Application.objects.filter(worker=worker)
            return ApplicationDocument.objects.filter(application__in=applications).order_by('-created_at')
        except Worker.DoesNotExist:
            return ApplicationDocument.objects.none()