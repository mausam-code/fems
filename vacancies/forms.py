from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Vacancy, Company, Country, JobCategory, Skill, VacancyAttachment

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'description', 'website', 'logo',
            'address', 'contact_email', 'contact_phone', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class VacancyForm(forms.ModelForm):
    skills_required = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Vacancy
        fields = [
            'title', 'company', 'category', 'country',
            'location', 'description', 'requirements', 'responsibilities',
            'benefits', 'salary_min', 'salary_max', 'currency',
            'is_salary_visible', 'employment_type', 'experience_required',
            'education_required', 'skills_required', 'application_deadline',
            'posted_date', 'status', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 5}),
            'responsibilities': forms.Textarea(attrs={'rows': 5}),
            'benefits': forms.Textarea(attrs={'rows': 5}),
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
            'posted_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name', 'code']

class JobCategoryForm(forms.ModelForm):
    class Meta:
        model = JobCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class VacancyAttachmentForm(forms.ModelForm):
    class Meta:
        model = VacancyAttachment
        fields = ['title', 'file']