from django.db import models
from django.conf import settings
import uuid

class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker = models.ForeignKey('workers.Worker', on_delete=models.CASCADE, related_name='applications')
    vacancy = models.ForeignKey('vacancies.Vacancy', on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=50, choices=[
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Interview Scheduled', 'Interview Scheduled'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
        ('Withdrawn', 'Withdrawn'),
    ], default='Draft')
    application_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability_date = models.DateField(null=True, blank=True)
    cover_letter = models.TextField(null=True, blank=True)
    is_terms_accepted = models.BooleanField(default=False)
    
    # Application form sections
    personal_info_completed = models.BooleanField(default=False)
    education_completed = models.BooleanField(default=False)
    experience_completed = models.BooleanField(default=False)
    documents_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Application for {self.vacancy.title} by {self.worker.user.first_name} {self.worker.user.last_name}"

class ApplicationDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=100, choices=[
        ('CV', 'CV'),
        ('Cover Letter', 'Cover Letter'),
        ('Passport', 'Passport'),
        ('ID Card', 'ID Card'),
        ('Educational Certificate', 'Educational Certificate'),
        ('Experience Certificate', 'Experience Certificate'),
        ('Medical Certificate', 'Medical Certificate'),
        ('Other', 'Other'),
    ])
    document = models.FileField(upload_to='application_documents/')
    description = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.document_type} for {self.application}"

class ApplicationNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='application_notes')
    note = models.TextField()
    is_private = models.BooleanField(default=True)  # Private notes are only visible to employees
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Note by {self.author.email} on {self.application}"

class ApplicationStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='status_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.application} - {self.status} on {self.changed_at}"
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Application status histories'
