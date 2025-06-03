from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View, CreateView, UpdateView, FormView, TemplateView
from django.urls import reverse_lazy

from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer
from .forms import LoginForm, RegisterForm, UserProfileForm, CustomPasswordChangeForm

User = get_user_model()

# API Views
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check old password
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Update token
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        
        return Response({
            "message": "Password updated successfully",
            "token": token.key
        }, status=status.HTTP_200_OK)

# Template Views
class LoginTemplateView(View):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            
            # Remember me functionality
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        
        return render(request, self.template_name, {'form': form})

class RegisterTemplateView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully! Please log in.")
        return response

class LogoutTemplateView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('accounts:login')

class ProfileTemplateView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profile updated successfully!")
        return response

class ChangePasswordTemplateView(LoginRequiredMixin, FormView):
    template_name = 'accounts/change_password.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('accounts:login')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Password changed successfully! Please log in again.")
        logout(self.request)
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Add user-specific data to context
        context['user'] = user
        
        # Add statistics based on user type
        if user.user_type == 'admin':
            # Admin statistics
            from applications.models import Application
            from workers.models import Worker
            from vacancies.models import Vacancy, Company
            
            context['total_workers'] = Worker.objects.count()
            context['total_companies'] = Company.objects.count()
            context['total_applications'] = Application.objects.count()
            context['total_vacancies'] = Vacancy.objects.count()
        elif user.user_type == 'worker':
            # Worker statistics
            from applications.models import Application
            from documents.models import Document
            from vacancies.models import Vacancy
            
            try:
                worker = user.worker_profile
                context['total_applications'] = Application.objects.filter(worker=worker).count()
                context['total_documents'] = Document.objects.filter(user=user).count()  # Fixed: Document is linked to user, not worker
                context['total_interviews'] = Application.objects.filter(worker=worker, status='Interview Scheduled').count()
                context['total_offers'] = Application.objects.filter(worker=worker, status='Selected').count()
            except:
                # Handle case where worker profile doesn't exist yet
                context['total_applications'] = 0
                context['total_documents'] = 0
                context['total_interviews'] = 0
                context['total_offers'] = 0
        elif user.user_type == 'employee':
            # Employee statistics
            from applications.models import Application
            from vacancies.models import Vacancy
            
            try:
                employee = user.employee_profile
                # Get counts based on employee permissions
                context['total_vacancies'] = Vacancy.objects.count()
                context['total_applications'] = Application.objects.count()
                context['total_interviews'] = Application.objects.filter(status='Interview Scheduled').count()
                context['total_placements'] = Application.objects.filter(status='Selected').count()
            except:
                # Handle case where employee profile doesn't exist yet
                context['total_vacancies'] = 0
                context['total_applications'] = 0
                context['total_interviews'] = 0
                context['total_placements'] = 0
        
        return context
