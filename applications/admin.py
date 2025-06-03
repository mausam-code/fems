from django.contrib import admin
from .models import Application, ApplicationDocument, ApplicationNote, ApplicationStatusHistory

class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0
    readonly_fields = ['verified_by', 'verification_date']  # Fixed: verified_date -> verification_date

class ApplicationNoteInline(admin.TabularInline):
    model = ApplicationNote
    extra = 0
    readonly_fields = ['author', 'created_at']  # Fixed: created_by -> author

class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ['changed_by', 'changed_at']
    ordering = ['-changed_at']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'worker_name', 'vacancy_title', 'status', 'application_date', 'last_updated']
    list_filter = ['status', 'application_date', 'last_updated', 'vacancy__company']
    search_fields = ['worker__user__first_name', 'worker__user__last_name', 'worker__user__email', 'vacancy__title']
    date_hierarchy = 'application_date'
    readonly_fields = ['application_date', 'last_updated']
    inlines = [ApplicationDocumentInline, ApplicationNoteInline, ApplicationStatusHistoryInline]
    
    def worker_name(self, obj):
        return f"{obj.worker.user.first_name} {obj.worker.user.last_name}"
    worker_name.short_description = 'Worker'
    
    def vacancy_title(self, obj):
        return obj.vacancy.title
    vacancy_title.short_description = 'Vacancy'

@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'application', 'document_type', 'is_verified', 'verified_by', 'verification_date']
    list_filter = ['document_type', 'is_verified', 'verification_date']
    search_fields = ['application__worker__user__first_name', 'application__worker__user__last_name']
    readonly_fields = ['verified_by', 'verification_date']

@admin.register(ApplicationNote)
class ApplicationNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'application', 'author_display', 'created_at', 'is_private']  # Fixed: created_by -> author_display
    list_filter = ['is_private', 'created_at']
    search_fields = ['application__worker__user__first_name', 'application__worker__user__last_name', 'note']
    readonly_fields = ['author', 'created_at']  # Fixed: created_by -> author

    def author_display(self, obj):
        return obj.author.email  # Display author's email or customize as needed
    author_display.short_description = 'Author'

@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'application', 'status_display', 'changed_by', 'changed_at']  # Fixed: removed previous_status, current_status
    list_filter = ['status', 'changed_at']
    search_fields = ['application__worker__user__first_name', 'application__worker__user__last_name']
    readonly_fields = ['changed_by', 'changed_at']
    ordering = ['-changed_at']

    def status_display(self, obj):
        return obj.status  # Display the status field
    status_display.short_description = 'Status'