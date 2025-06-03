from rest_framework import serializers
from .models import Worker, WorkerEducation, WorkerExperience, WorkerSkill
from django.contrib.auth import get_user_model

User = get_user_model()

class WorkerSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerSkill
        fields = ['id', 'name', 'level', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class WorkerEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerEducation
        fields = ['id', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date', 
                  'is_current', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class WorkerExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerExperience
        fields = ['id', 'company', 'position', 'location', 'start_date', 'end_date', 
                  'is_current', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class WorkerSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    educations = WorkerEducationSerializer(many=True, read_only=True)
    experiences = WorkerExperienceSerializer(many=True, read_only=True)
    skills = WorkerSkillSerializer(source='skill_list', many=True, read_only=True)
    
    class Meta:
        model = Worker
        fields = ['id', 'user_email', 'user_first_name', 'user_last_name', 'user_phone_number',
                  'date_of_birth', 'gender', 'nationality', 'passport_number', 'passport_expiry',
                  'address', 'skills', 'experience_years', 'education_level', 'preferred_job_type',
                  'preferred_country', 'profile_picture', 'cv_file', 'created_at', 'updated_at',
                  'educations', 'experiences', 'skills']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class WorkerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['date_of_birth', 'gender', 'nationality', 'passport_number', 'passport_expiry',
                  'address', 'skills', 'experience_years', 'education_level', 'preferred_job_type',
                  'preferred_country', 'profile_picture', 'cv_file']

class WorkerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['date_of_birth', 'gender', 'nationality', 'passport_number', 'passport_expiry',
                  'address', 'skills', 'experience_years', 'education_level', 'preferred_job_type',
                  'preferred_country', 'profile_picture', 'cv_file']