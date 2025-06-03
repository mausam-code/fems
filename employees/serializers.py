from rest_framework import serializers
from .models import Employee, EmployeePermission
from django.contrib.auth import get_user_model

User = get_user_model()

class EmployeePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeePermission
        fields = ['id', 'can_verify_workers', 'can_verify_applications', 'can_manage_vacancies',
                  'can_manage_companies', 'can_manage_countries', 'can_manage_documents',
                  'can_manage_employees', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class EmployeeSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    permissions = EmployeePermissionSerializer(read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'user_email', 'user_first_name', 'user_last_name', 'user_phone_number',
                  'employee_id', 'department', 'position', 'date_of_birth', 'gender',
                  'address', 'profile_picture', 'date_joined', 'is_active', 'created_at', 'updated_at',
                  'permissions']
        read_only_fields = ['id', 'created_at', 'updated_at']

class EmployeeCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Employee
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password',
                  'employee_id', 'department', 'position', 'date_of_birth', 'gender',
                  'address', 'profile_picture', 'date_joined', 'is_active']
    
    def create(self, validated_data):
        email = validated_data.pop('email')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        phone_number = validated_data.pop('phone_number', '')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            user_type='employee'
        )
        
        employee = Employee.objects.create(user=user, **validated_data)
        EmployeePermission.objects.create(employee=employee)
        
        return employee

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source='user.first_name', required=False)
    user_last_name = serializers.CharField(source='user.last_name', required=False)
    user_phone_number = serializers.CharField(source='user.phone_number', required=False, allow_blank=True)
    
    class Meta:
        model = Employee
        fields = ['user_first_name', 'user_last_name', 'user_phone_number',
                  'department', 'position', 'date_of_birth', 'gender',
                  'address', 'profile_picture', 'date_joined', 'is_active']
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if 'phone_number' in user_data:
            user.phone_number = user_data['phone_number']
        
        user.save()
        
        return super().update(instance, validated_data)

class EmployeePermissionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeePermission
        fields = ['can_verify_workers', 'can_verify_applications', 'can_manage_vacancies',
                  'can_manage_companies', 'can_manage_countries', 'can_manage_documents',
                  'can_manage_employees']