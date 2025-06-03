from django import forms
from .models import Employee, EmployeePermission

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'department', 'position', 'date_of_birth',
            'gender', 'address', 'profile_picture', 'date_joined', 'is_active'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class EmployeePermissionForm(forms.ModelForm):
    class Meta:
        model = EmployeePermission
        fields = [
            'can_verify_workers', 'can_verify_applications',
            'can_manage_vacancies', 'can_manage_companies',
            'can_manage_countries', 'can_manage_documents',
            'can_manage_employees'
        ]
        widgets = {
            'can_verify_workers': forms.CheckboxInput(),
            'can_verify_applications': forms.CheckboxInput(),
            'can_manage_vacancies': forms.CheckboxInput(),
            'can_manage_companies': forms.CheckboxInput(),
            'can_manage_countries': forms.CheckboxInput(),
            'can_manage_documents': forms.CheckboxInput(),
            'can_manage_employees': forms.CheckboxInput(),
        }