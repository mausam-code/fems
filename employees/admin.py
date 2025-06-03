from django.contrib import admin
from .models import Employee, EmployeePermission

class EmployeePermissionInline(admin.StackedInline):
    model = EmployeePermission
    can_delete = False
    verbose_name_plural = 'Permissions'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_name', 'get_email', 'employee_id', 'department', 'position', 'is_active', 'created_at')
    list_filter = ('is_active', 'department', 'position', 'gender')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'employee_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [EmployeePermissionInline]
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(EmployeePermission)
class EmployeePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'can_verify_workers', 'can_verify_applications', 
                    'can_manage_vacancies', 'can_manage_companies', 'can_manage_employees')
    list_filter = ('can_verify_workers', 'can_verify_applications', 'can_manage_vacancies', 
                   'can_manage_companies', 'can_manage_employees')
    search_fields = ('employee__user__email', 'employee__employee_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
