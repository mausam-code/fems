from rest_framework import serializers
from .models import Application, ApplicationDocument, ApplicationNote, ApplicationStatusHistory
from workers.serializers import WorkerSerializer
from django.utils import timezone

class ApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = ['id', 'document_type', 'document', 'description', 'is_verified', 
                  'verification_date', 'verified_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_verified', 'verification_date', 'verified_by', 'created_at', 'updated_at']

class ApplicationNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationNote
        fields = ['id', 'note', 'is_private', 'author', 'author_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'author_name', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"

class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ApplicationStatusHistory
        fields = ['id', 'status', 'changed_by', 'changed_by_name', 'changed_at', 'remarks']
        read_only_fields = ['id', 'changed_by', 'changed_by_name', 'changed_at']
    
    def get_changed_by_name(self, obj):
        return f"{obj.changed_by.first_name} {obj.changed_by.last_name}"

class ApplicationSerializer(serializers.ModelSerializer):
    documents = ApplicationDocumentSerializer(many=True, read_only=True)
    notes = serializers.SerializerMethodField()
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    worker_details = serializers.SerializerMethodField()
    vacancy_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = ['id', 'worker', 'worker_details', 'vacancy', 'vacancy_details', 'status', 
                  'application_date', 'last_updated', 'expected_salary', 'availability_date', 
                  'cover_letter', 'is_terms_accepted', 'personal_info_completed', 
                  'education_completed', 'experience_completed', 'documents_completed', 
                  'created_at', 'updated_at', 'documents', 'notes', 'status_history']
        read_only_fields = ['id', 'application_date', 'last_updated', 'created_at', 'updated_at']
    
    def get_notes(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return []
        
        # If the user is a worker, only return non-private notes
        if hasattr(request.user, 'worker_profile'):
            notes = obj.notes.filter(is_private=False)
        else:
            notes = obj.notes.all()
        
        return ApplicationNoteSerializer(notes, many=True).data
    
    def get_worker_details(self, obj):
        return {
            'id': obj.worker.id,
            'name': f"{obj.worker.user.first_name} {obj.worker.user.last_name}",
            'email': obj.worker.user.email,
            'phone': obj.worker.user.phone_number,
        }
    
    def get_vacancy_details(self, obj):
        return {
            'id': obj.vacancy.id,
            'title': obj.vacancy.title,
            'company': obj.vacancy.company.name if obj.vacancy.company else None,
            'location': obj.vacancy.location,
        }

class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['vacancy', 'expected_salary', 'availability_date', 'cover_letter']
    
    def create(self, validated_data):
        request = self.context.get('request')
        worker = request.user.worker_profile
        
        application = Application.objects.create(
            worker=worker,
            **validated_data
        )
        
        return application

class ApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['expected_salary', 'availability_date', 'cover_letter', 'is_terms_accepted',
                  'personal_info_completed', 'education_completed', 'experience_completed', 
                  'documents_completed']

class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    remarks = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Application
        fields = ['status', 'remarks']
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        remarks = validated_data.pop('remarks', '')
        
        # Update the application status
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        instance = super().update(instance, validated_data)
        
        # Create status history entry if status changed
        if old_status != new_status:
            ApplicationStatusHistory.objects.create(
                application=instance,
                status=new_status,
                changed_by=request.user,
                remarks=remarks
            )
        
        return instance

class ApplicationDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = ['document_type', 'document', 'description']
    
    def create(self, validated_data):
        application = self.context.get('application')
        
        document = ApplicationDocument.objects.create(
            application=application,
            **validated_data
        )
        
        return document

class ApplicationDocumentVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = ['is_verified']
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        
        if validated_data.get('is_verified', False):
            instance.is_verified = True
            instance.verification_date = timezone.now()
            instance.verified_by = request.user
        else:
            instance.is_verified = False
            instance.verification_date = None
            instance.verified_by = None
        
        instance.save()
        return instance

class ApplicationNoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationNote
        fields = ['note', 'is_private']
    
    def create(self, validated_data):
        request = self.context.get('request')
        application = self.context.get('application')
        
        note = ApplicationNote.objects.create(
            application=application,
            author=request.user,
            **validated_data
        )
        
        return note