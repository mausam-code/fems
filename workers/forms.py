from django import forms
from .models import Worker, WorkerEducation, WorkerExperience, WorkerSkill

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = [
            'date_of_birth', 'gender', 'nationality', 'passport_number',
            'passport_expiry', 'address', 'skills', 'experience_years',
            'education_level', 'preferred_job_type', 'preferred_country',
            'profile_picture', 'cv_file'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'passport_expiry': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.Textarea(attrs={'rows': 3}),
        }

class WorkerEducationForm(forms.ModelForm):
    class Meta:
        model = WorkerEducation
        fields = [
            'institution', 'degree', 'field_of_study',
            'start_date', 'end_date', 'is_current', 'description'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')

        if is_current and end_date:
            self.add_error('end_date', 'End date should be empty if this is your current education')
        elif not is_current and not end_date:
            self.add_error('end_date', 'End date is required if this is not your current education')

        return cleaned_data

class WorkerExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkerExperience
        fields = [
            'company', 'position', 'location',
            'start_date', 'end_date', 'is_current', 'description'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_current = cleaned_data.get('is_current')
        end_date = cleaned_data.get('end_date')

        if is_current and end_date:
            self.add_error('end_date', 'End date should be empty if this is your current job')
        elif not is_current and not end_date:
            self.add_error('end_date', 'End date is required if this is not your current job')

        return cleaned_data

class WorkerSkillForm(forms.ModelForm):
    class Meta:
        model = WorkerSkill
        fields = ['name', 'level']