from django.contrib import admin
from .models import SchoolLevel, AcademicYear, Term, Classroom

@admin.register(SchoolLevel)
class SchoolLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_editable = ('is_current',)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('number', 'academic_year', 'start_date', 'end_date')
    list_filter = ('academic_year',)

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'academic_year', 'capacity')
    list_filter = ('level', 'academic_year')
