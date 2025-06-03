from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Application, ApplicationDocument, ApplicationNote, ApplicationStatusHistory
from workers.models import Worker
from .forms import ApplicationForm, ApplicationStatusForm, ApplicationDocumentForm

class ApplicationAccessMixin(LoginRequiredMixin):
    """Mixin to ensure proper access control for application views"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Allow staff
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        
        # Check if user is an employee with application verification permission
        if hasattr(request.user, 'employee_profile') and request.user.employee_profile.permissions.can_verify_applications:
            return super().dispatch(request, *args, **kwargs)
        
        # For workers, check if they own the application
        if request.user.user_type == 'worker' and hasattr(self, 'get_object'):
            obj = self.get_object()
            if obj.worker.user == request.user:
                return super().dispatch(request, *args, **kwargs)
        
        # For list views, the queryset will be filtered in get_queryset
        if not hasattr(self, 'get_object'):
            return super().dispatch(request, *args, **kwargs)
        
        # Redirect to dashboard if not authorized
        return redirect('dashboard')

class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'
    
    def get_queryset(self):
        user = self.request.user
        
        # Staff and employees with verification permission can see all applications
        if user.is_staff or (hasattr(user, 'employee_profile') and 
                           user.employee_profile.permissions.can_verify_applications):
            return Application.objects.all().order_by('-created_at')
        
        # Workers can only see their own applications
        if user.user_type == 'worker':
            try:
                worker = Worker.objects.get(user=user)
                return Application.objects.filter(worker=worker).order_by('-created_at')
            except Worker.DoesNotExist:
                pass
        
        return Application.objects.none()

class ApplicationDetailView(ApplicationAccessMixin, DetailView):
    model = Application
    template_name = 'applications/application_detail.html'
    context_object_name = 'application'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()
        
        # Add documents to context
        context['documents'] = ApplicationDocument.objects.filter(application=application)
        
        # Add notes to context, filtering private notes for workers
        if self.request.user.user_type == 'worker':
            context['notes'] = ApplicationNote.objects.filter(
                application=application, is_private=False
            ).order_by('-created_at')
        else:
            context['notes'] = ApplicationNote.objects.filter(
                application=application
            ).order_by('-created_at')
        
        # Add status history to context
        context['status_history'] = ApplicationStatusHistory.objects.filter(
            application=application
        ).order_by('-created_at')
        
        # Add status form for employees and staff
        if self.request.user.is_staff or (hasattr(self.request.user, 'employee_profile') and 
                                        self.request.user.employee_profile.permissions.can_verify_applications):
            context['status_form'] = ApplicationStatusForm(instance=application)
        
        return context

class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'applications/application_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Only workers can create applications
        if not request.user.is_authenticated or request.user.user_type != 'worker':
            messages.error(request, "Only workers can create applications.")
            return redirect('dashboard')
        
        # Check if worker profile exists
        try:
            Worker.objects.get(user=request.user)
        except Worker.DoesNotExist:
            messages.error(request, "You need to create a worker profile first.")
            return redirect('workers:worker_create')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.worker = Worker.objects.get(user=self.request.user)
        form.instance.status = 'pending'
        response = super().form_valid(form)
        
        # Create initial status history entry
        ApplicationStatusHistory.objects.create(
            application=self.object,
            status='pending',
            changed_by=self.request.user,
            notes="Application submitted"
        )
        
        messages.success(self.request, "Application submitted successfully.")
        return response
    
    def get_success_url(self):
        return reverse_lazy('applications:application_detail', kwargs={'pk': self.object.pk})

class ApplicationUpdateView(ApplicationAccessMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'applications/application_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        application = self.get_object()
        
        # Only allow updates for pending applications
        if application.status != 'pending':
            messages.error(request, "You can only update pending applications.")
            return redirect('applications:application_detail', pk=application.pk)
        
        # Only the worker who created the application can update it
        if request.user.user_type == 'worker' and application.worker.user != request.user:
            messages.error(request, "You can only update your own applications.")
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('applications:application_detail', kwargs={'pk': self.object.pk})

class ApplicationStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationStatusForm
    template_name = 'applications/application_status_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Only staff and employees with verification permission can update status
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not (request.user.is_staff or (hasattr(request.user, 'employee_profile') and 
                                        request.user.employee_profile.permissions.can_verify_applications)):
            messages.error(request, "You don't have permission to update application status.")
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        old_status = self.get_object().status
        new_status = form.cleaned_data['status']
        notes = form.cleaned_data.get('notes', '')
        
        response = super().form_valid(form)
        
        # Create status history entry if status changed
        if old_status != new_status:
            ApplicationStatusHistory.objects.create(
                application=self.object,
                status=new_status,
                changed_by=self.request.user,
                notes=notes
            )
            
            status_display = dict(Application.STATUS_CHOICES).get(new_status, new_status)
            messages.success(self.request, f"Application status updated to {status_display}.")
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('applications:application_detail', kwargs={'pk': self.object.pk})

class ApplicationDocumentListView(LoginRequiredMixin, ListView):
    template_name = 'applications/application_document_list.html'
    context_object_name = 'documents'
    
    def dispatch(self, request, *args, **kwargs):
        self.application = get_object_or_404(Application, pk=self.kwargs['application_id'])
        
        # Check permissions
        if request.user.is_staff or (hasattr(request.user, 'employee_profile') and 
                                   request.user.employee_profile.permissions.can_verify_applications):
            return super().dispatch(request, *args, **kwargs)
        
        if request.user.user_type == 'worker' and self.application.worker.user == request.user:
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, "You don't have permission to view these documents.")
        return redirect('dashboard')
    
    def get_queryset(self):
        return ApplicationDocument.objects.filter(application=self.application).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.application
        return context

class ApplicationDocumentCreateView(LoginRequiredMixin, CreateView):
    model = ApplicationDocument
    form_class = ApplicationDocumentForm
    template_name = 'applications/application_document_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.application = get_object_or_404(Application, pk=self.kwargs['application_id'])
        
        # Only the worker who owns the application can add documents
        if request.user.user_type != 'worker' or self.application.worker.user != request.user:
            messages.error(request, "You don't have permission to add documents to this application.")
            return redirect('applications:application_detail', pk=self.application.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.application = self.application
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        
        messages.success(self.request, "Document uploaded successfully.")
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.application
        return context
    
    def get_success_url(self):
        return reverse_lazy('applications:application_document_list', 
                           kwargs={'application_id': self.application.pk})

class ApplicationDocumentVerifyView(LoginRequiredMixin, UpdateView):
    model = ApplicationDocument
    fields = ['is_verified', 'verification_notes']
    template_name = 'applications/application_document_verify_form.html'
    context_object_name = 'document'
    
    def dispatch(self, request, *args, **kwargs):
        # Only staff and employees with verification permission can verify documents
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not (request.user.is_staff or (hasattr(request.user, 'employee_profile') and 
                                        request.user.employee_profile.permissions.can_verify_applications)):
            messages.error(request, "You don't have permission to verify documents.")
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.verified_by = self.request.user
        form.instance.verified_at = timezone.now()
        response = super().form_valid(form)
        
        status = "verified" if form.instance.is_verified else "rejected"
        messages.success(self.request, f"Document {status} successfully.")
        return response
    
    def get_success_url(self):
        return reverse_lazy('applications:application_document_list', 
                           kwargs={'application_id': self.object.application.pk})