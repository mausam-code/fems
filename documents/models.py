from django.db import models
from django.conf import settings
import uuid

class Document(models.Model):
    """Model for storing documents uploaded by users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    document_type = models.CharField(max_length=50, choices=[
        ('passport', 'Passport'),
        ('id_card', 'ID Card'),
        ('certificate', 'Certificate'),
        ('other', 'Other')
    ])
    extracted_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
