from django.contrib import admin
from .models import Worker, WorkerEducation, WorkerExperience, WorkerSkill

class WorkerEducationInline(admin.TabularInline):
    model = WorkerEducation
    extra = 0

class WorkerExperienceInline(admin.TabularInline):
    model = WorkerExperience
    extra = 0

class WorkerSkillInline(admin.TabularInline):
    model = WorkerSkill
    extra = 0

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_name', 'get_email', 'nationality', 'experience_years', 'created_at')
    list_filter = ('gender', 'nationality', 'preferred_country')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'passport_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [WorkerEducationInline, WorkerExperienceInline, WorkerSkillInline]
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(WorkerEducation)
class WorkerEducationAdmin(admin.ModelAdmin):
    list_display = ('id', 'worker', 'institution', 'degree', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('worker__user__email', 'institution', 'degree')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(WorkerExperience)
class WorkerExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'worker', 'company', 'position', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('worker__user__email', 'company', 'position')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(WorkerSkill)
class WorkerSkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'worker', 'name', 'level')
    list_filter = ('level',)
    search_fields = ('worker__user__email', 'name')
    readonly_fields = ('id', 'created_at', 'updated_at')
