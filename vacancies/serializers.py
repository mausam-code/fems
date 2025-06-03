from rest_framework import serializers
from .models import Company, JobCategory, Country, Skill, Vacancy, VacancyAttachment

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class VacancyAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = VacancyAttachment
        fields = ['id', 'vacancy', 'title', 'file', 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}"
        return None

class VacancyAttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyAttachment
        fields = ['title', 'file']
    
    def create(self, validated_data):
        vacancy = self.context.get('vacancy')
        request = self.context.get('request')
        
        attachment = VacancyAttachment.objects.create(
            vacancy=vacancy,
            title=validated_data['title'],
            file=validated_data['file'],
            uploaded_by=request.user if request else None
        )
        
        return attachment

class VacancyListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Vacancy
        fields = [
            'id', 'title', 'company', 'company_name', 'category', 'category_name',
            'country', 'country_name', 'location', 'employment_type', 'salary_min',
            'salary_max', 'currency', 'is_salary_visible', 'posted_date',
            'application_deadline', 'status', 'is_featured', 'is_open'
        ]

class VacancyDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    skills_required = SkillSerializer(many=True, read_only=True)
    attachments = VacancyAttachmentSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    is_open = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Vacancy
        fields = '__all__'
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
    
    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}"
        return None

class VacancyCreateSerializer(serializers.ModelSerializer):
    skills_required = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, required=False)
    
    class Meta:
        model = Vacancy
        exclude = ['created_by', 'updated_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        skills = validated_data.pop('skills_required', [])
        request = self.context.get('request')
        
        vacancy = Vacancy.objects.create(
            **validated_data,
            created_by=request.user if request else None,
            updated_by=request.user if request else None
        )
        
        if skills:
            vacancy.skills_required.set(skills)
        
        return vacancy

class VacancyUpdateSerializer(serializers.ModelSerializer):
    skills_required = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, required=False)
    
    class Meta:
        model = Vacancy
        exclude = ['created_by', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        skills = validated_data.pop('skills_required', None)
        request = self.context.get('request')
        
        # Update the updated_by field
        instance.updated_by = request.user if request else None
        
        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Update skills if provided
        if skills is not None:
            instance.skills_required.set(skills)
        
        return instance