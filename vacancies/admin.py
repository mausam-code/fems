from django.contrib import admin
from .models import Company, JobCategory, Country, Skill, Vacancy, VacancyAttachment

class VacancyAttachmentInline(admin.TabularInline):
    model = VacancyAttachment
    extra = 0
    readonly_fields = ['uploaded_by', 'uploaded_at']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'contact_email', 'contact_phone', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'contact_email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'employment_type', 'status', 'posted_date', 'application_deadline', 'is_featured']
    list_filter = ['status', 'employment_type', 'is_featured', 'posted_date', 'application_deadline', 'company']
    search_fields = ['title', 'description', 'requirements', 'responsibilities', 'location']
    readonly_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']
    filter_horizontal = ['skills_required']
    date_hierarchy = 'posted_date'
    inlines = [VacancyAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'category', 'country', 'location', 'status', 'is_featured')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'responsibilities', 'benefits')
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max', 'currency', 'is_salary_visible')
        }),
        ('Requirements', {
            'fields': ('employment_type', 'experience_required', 'education_required', 'skills_required')
        }),
        ('Dates', {
            'fields': ('posted_date', 'application_deadline')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(VacancyAttachment)
class VacancyAttachmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'vacancy', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['title', 'vacancy__title']
    readonly_fields = ['uploaded_by', 'uploaded_at']
