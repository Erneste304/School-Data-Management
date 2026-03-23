from django.shortcuts import render, get_object_or_404
from .models import SchoolLevel, AcademicYear, Term, Classroom

def school_info_view(request):
    levels = SchoolLevel.objects.all()
    current_year = AcademicYear.objects.filter(is_current=True).first()
    classrooms = Classroom.objects.filter(academic_year=current_year)
    return render(request, 'schools/info.html', {
        'levels': levels,
        'current_year': current_year,
        'classrooms': classrooms
    })
