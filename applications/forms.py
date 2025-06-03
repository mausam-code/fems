from django import forms
from .models import Application, ApplicationDocument, ApplicationNote, ApplicationStatusHistory

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'expected_salary', 'availability_date', 'cover_letter',
            'is_terms_accepted'
        ]
        widgets = {
            'availability_date': forms.DateInput(attrs={'type': 'date'}),
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
        }

class ApplicationStatusForm(forms.ModelForm):
    remarks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = Application
        fields = ['status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget = forms.Select(choices=[
            ('Draft', 'Draft'),
            ('Submitted', 'Submitted'),
            ('Under Review', 'Under Review'),
            ('Interview Scheduled', 'Interview Scheduled'),
            ('Selected', 'Selected'),
            ('Rejected', 'Rejected'),
            ('Withdrawn', 'Withdrawn'),
        ])

class ApplicationDocumentForm(forms.ModelForm):
    class Meta:
        model = ApplicationDocument
        fields = ['document_type', 'document', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Brief description of the document'}),
        }

class ApplicationNoteForm(forms.ModelForm):
    class Meta:
        model = ApplicationNote
        fields = ['note', 'is_private']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

class ApplicationStatusHistoryForm(forms.ModelForm):
    class Meta:
        model = ApplicationStatusHistory
        fields = ['status', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }