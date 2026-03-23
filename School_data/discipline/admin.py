from django.contrib import admin
from .models import (
    DisciplineCategory, DisciplineCase, DisciplineAction, 
    DisciplineHearing, DisciplineRecord, IncidentReport
)

class DisciplineActionInline(admin.TabularInline):
    model = DisciplineAction
    extra = 1
    fields = ['action_type', 'description', 'due_date', 'is_completed']

class DisciplineCaseAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'student', 'category', 'status', 'incident_date', 'reported_date']
    list_filter = ['status', 'category', 'incident_date']
    search_fields = ['case_number', 'student__full_name', 'student__admission_number']
    readonly_fields = ['case_number', 'reported_date', 'last_updated']
    inlines = [DisciplineActionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('case_number', 'student', 'category', 'incident_date', 'incident_location')
        }),
        ('Details', {
            'fields': ('description', 'evidence', 'reported_by')
        }),
        ('Status', {
            'fields': ('status', 'assigned_to', 'resolved_date')
        }),
    )

class DisciplineCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity', 'points', 'default_action']
    list_filter = ['severity']
    search_fields = ['name']

class DisciplineRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'total_points', 'total_cases', 'is_on_probation']
    list_filter = ['academic_year', 'is_on_probation']
    search_fields = ['student__full_name', 'student__admission_number']
    readonly_fields = ['total_points', 'total_cases', 'major_cases', 'minor_cases']

class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_date', 'period', 'created_by']
    list_filter = ['period', 'report_date']
    filter_horizontal = ['cases_included']

admin.site.register(DisciplineCategory, DisciplineCategoryAdmin)
admin.site.register(DisciplineCase, DisciplineCaseAdmin)
admin.site.register(DisciplineAction)
admin.site.register(DisciplineHearing)
admin.site.register(DisciplineRecord, DisciplineRecordAdmin)
admin.site.register(IncidentReport, IncidentReportAdmin)
