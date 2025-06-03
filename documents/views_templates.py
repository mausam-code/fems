from django.views.generic import FormView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django import forms
import json
from .models import Document
from services.document_scanner import DocumentScanner

class DocumentScannerForm(forms.Form):
    document = forms.ImageField(help_text="Upload a document image to scan")
    document_type = forms.ChoiceField(choices=[
        ('passport', 'Passport'),
        ('id_card', 'ID Card'),
        ('certificate', 'Certificate'),
        ('other', 'Other')
    ])

class DocumentScannerView(LoginRequiredMixin, FormView):
    template_name = 'documents/scanner.html'
    form_class = DocumentScannerForm
    success_url = reverse_lazy('documents:scanner_results')
    
    def form_valid(self, form):
        # Save the uploaded document
        document_file = form.cleaned_data['document']
        document_type = form.cleaned_data['document_type']
        
        # Create a new document record
        document = Document.objects.create(
            user=self.request.user,
            file=document_file,
            document_type=document_type,
            name=f"{document_type.capitalize()} - {document_file.name}"
        )
        
        # Process the document with OCR
        try:
            if document_type == 'passport':
                passport_info = DocumentScanner.extract_passport_info(document.file.path)
                self.request.session['passport_info'] = passport_info
                
                # Save the extracted passport info to the document model
                document.extracted_text = json.dumps(passport_info)
                document.save()
            else:
                extracted_text = DocumentScanner.extract_text(document.file.path)
                self.request.session['extracted_text'] = extracted_text
                
                # Save the extracted text to the document model
                document.extracted_text = extracted_text
                document.save()
            
            self.request.session['document_id'] = str(document.id)
            messages.success(self.request, 'Document scanned successfully')
        except Exception as e:
            messages.error(self.request, f'Error scanning document: {str(e)}')
        
        return super().form_valid(form)

class ScannerResultsView(LoginRequiredMixin, TemplateView):
    template_name = 'documents/scanner_results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        document_id = self.request.session.get('document_id')
        if document_id:
            try:
                context['document'] = Document.objects.get(id=document_id)
                
                # Get the extracted information
                context['passport_info'] = self.request.session.get('passport_info')
                context['extracted_text'] = self.request.session.get('extracted_text')
                
                # Clear the session data
                if 'passport_info' in self.request.session:
                    del self.request.session['passport_info']
                if 'extracted_text' in self.request.session:
                    del self.request.session['extracted_text']
                if 'document_id' in self.request.session:
                    del self.request.session['document_id']
            except Document.DoesNotExist:
                messages.error(self.request, 'Document not found')
        
        return context

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by('-created_at')

class DocumentDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'documents/document_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = get_object_or_404(Document, id=self.kwargs['pk'], user=self.request.user)
        context['document'] = document
        
        # If the document is a passport and has extracted text as JSON
        if document.document_type == 'passport' and document.extracted_text:
            try:
                context['passport_info'] = json.loads(document.extracted_text)
            except json.JSONDecodeError:
                context['extracted_text'] = document.extracted_text
        else:
            context['extracted_text'] = document.extracted_text
            
        return context