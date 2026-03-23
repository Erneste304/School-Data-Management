from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    DisciplineCategory, DisciplineCase, DisciplineAction, 
    DisciplineHearing, DisciplineRecord, IncidentReport
)
from academics.models import Student
from schools.models import AcademicYear
from accounts.views import role_required
from .forms import (
    DisciplineCaseForm, DisciplineActionForm, 
    HearingForm, IncidentReportForm
)

@login_required
@role_required(['head_teacher', 'dod', 'admin'])
def dashboard_view(request):
    """Discipline dashboard for DOD and Head Teacher"""
    # Get current academic year
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Statistics
    total_cases = DisciplineCase.objects.count()
    pending_cases = DisciplineCase.objects.filter(status__in=['reported', 'investigating']).count()
    resolved_cases = DisciplineCase.objects.filter(status='closed').count()
    
    # Cases by severity
    major_cases = DisciplineCase.objects.filter(
        category__severity__in=['major', 'critical']
    ).count()
    
    # Recent cases
    recent_cases = DisciplineCase.objects.all()[:10]
    
    # Students on probation
    probation_students = DisciplineRecord.objects.filter(
        academic_year=current_year,
        is_on_probation=True
    )[:10]
    
    # Cases by category
    cases_by_category = DisciplineCategory.objects.annotate(
        case_count=Count('disciplinecase')
    ).filter(case_count__gt=0)
    
    context = {
        'total_cases': total_cases,
        'pending_cases': pending_cases,
        'resolved_cases': resolved_cases,
        'major_cases': major_cases,
        'recent_cases': recent_cases,
        'probation_students': probation_students,
        'cases_by_category': cases_by_category,
    }
    return render(request, 'discipline/dashboard.html', context)

@login_required
@role_required(['head_teacher', 'dod', 'admin'])
def case_list_view(request):
    """List all discipline cases with filters"""
    cases = DisciplineCase.objects.select_related('student', 'category', 'reported_by')
    
    # Apply filters
    status = request.GET.get('status')
    if status:
        cases = cases.filter(status=status)
    
    category = request.GET.get('category')
    if category:
        cases = cases.filter(category_id=category)
    
    student = request.GET.get('student')
    if student:
        cases = cases.filter(student__full_name__icontains=student)
    
    date_from = request.GET.get('date_from')
    if date_from:
        cases = cases.filter(incident_date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        cases = cases.filter(incident_date__lte=date_to)
    
    context = {
        'cases': cases,
        'categories': DisciplineCategory.objects.all(),
        'status_choices': DisciplineCase.STATUS_CHOICES,
        'filters': request.GET,
    }
    return render(request, 'discipline/case_list.html', context)

@login_required
@role_required(['head_teacher', 'dod', 'admin'])
def case_detail_view(request, pk):
    """View discipline case details"""
    case = get_object_or_404(DisciplineCase, pk=pk)
    actions = case.actions.all()
    
    context = {
        'case': case,
        'actions': actions,
        'has_hearing': hasattr(case, 'hearing'),
    }
    return render(request, 'discipline/case_detail.html', context)

@login_required
@role_required(['head_teacher', 'dod', 'teacher'])
def case_create_view(request):
    """Create a new discipline case"""
    if request.method == 'POST':
        form = DisciplineCaseForm(request.POST, request.FILES)
        if form.is_valid():
            case = form.save(commit=False)
            case.reported_by = request.user
            case.save()
            messages.success(request, f'Case {case.case_number} created successfully')
            return redirect('discipline:case_detail', pk=case.pk)
    else:
        form = DisciplineCaseForm()
    
    return render(request, 'discipline/case_form.html', {'form': form})

@login_required
@role_required(['head_teacher', 'dod'])
def case_update_view(request, pk):
    """Update discipline case"""
    case = get_object_or_404(DisciplineCase, pk=pk)
    
    if request.method == 'POST':
        form = DisciplineCaseForm(request.POST, request.FILES, instance=case)
        if form.is_valid():
            case = form.save()
            messages.success(request, f'Case {case.case_number} updated successfully')
            return redirect('discipline:case_detail', pk=case.pk)
    else:
        form = DisciplineCaseForm(instance=case)
    
    return render(request, 'discipline/case_form.html', {'form': form, 'case': case})

@login_required
@role_required(['head_teacher', 'dod'])
def add_action_view(request, case_pk):
    """Add action to a discipline case"""
    case = get_object_or_404(DisciplineCase, pk=case_pk)
    
    if request.method == 'POST':
        form = DisciplineActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.case = case
            action.taken_by = request.user
            action.save()
            messages.success(request, 'Action added successfully')
            return redirect('discipline:case_detail', pk=case.pk)
    else:
        form = DisciplineActionForm()
    
    return render(request, 'discipline/add_action.html', {'form': form, 'case': case})

@login_required
@role_required(['head_teacher', 'dod'])
def schedule_hearing_view(request, case_pk):
    """Schedule a hearing for a discipline case"""
    case = get_object_or_404(DisciplineCase, pk=case_pk)
    
    if hasattr(case, 'hearing'):
        messages.warning(request, 'A hearing already exists for this case')
        return redirect('discipline:case_detail', pk=case.pk)
    
    if request.method == 'POST':
        form = HearingForm(request.POST)
        if form.is_valid():
            hearing = form.save(commit=False)
            hearing.case = case
            hearing.save()
            form.save_m2m()  # Save many-to-many committee members
            messages.success(request, 'Hearing scheduled successfully')
            return redirect('discipline:case_detail', pk=case.pk)
    else:
        form = HearingForm()
    
    return render(request, 'discipline/schedule_hearing.html', {'form': form, 'case': case})

@login_required
@role_required(['head_teacher', 'dod'])
def student_record_view(request, student_id):
    """View discipline record for a specific student"""
    student = get_object_or_404(Student, pk=student_id)
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    discipline_record, created = DisciplineRecord.objects.get_or_create(
        student=student,
        academic_year=current_year
    )
    
    cases = DisciplineCase.objects.filter(student=student)
    
    context = {
        'student': student,
        'record': discipline_record,
        'cases': cases,
    }
    return render(request, 'discipline/student_record.html', context)

@login_required
@role_required(['head_teacher', 'dod'])
def generate_report_view(request):
    """Generate incident report"""
    if request.method == 'POST':
        form = IncidentReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            form.save_m2m()
            messages.success(request, 'Report generated successfully')
            return redirect('discipline:report_detail', pk=report.pk)
    else:
        form = IncidentReportForm()
    
    return render(request, 'discipline/generate_report.html', {'form': form})

@login_required
@role_required(['head_teacher', 'dod'])
def analytics_view(request):
    """Discipline analytics and statistics"""
    # Get last 12 months
    end_date = timezone.now()
    start_date = end_date - timedelta(days=365)
    
    # Monthly case trends
    monthly_cases = DisciplineCase.objects.filter(
        reported_date__gte=start_date
    ).extra(
        {'month': "strftime('%%Y-%%m', reported_date)"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Cases by category
    cases_by_category = DisciplineCategory.objects.annotate(
        count=Count('disciplinecase')
    ).values('name', 'severity', 'count')
    
    # Most frequent offenders
    top_offenders = DisciplineCase.objects.values(
        'student__full_name', 'student__admission_number'
    ).annotate(
        case_count=Count('id')
    ).order_by('-case_count')[:10]
    
    # Resolution time analysis
    resolved_cases = DisciplineCase.objects.filter(
        status='closed',
        resolved_date__isnull=False
    )
    
    avg_resolution_time = 0
    if resolved_cases.exists():
        total_days = sum(
            (case.resolved_date - case.reported_date).days 
            for case in resolved_cases
        )
        avg_resolution_time = total_days / resolved_cases.count()
    
    context = {
        'monthly_cases': list(monthly_cases),
        'cases_by_category': cases_by_category,
        'top_offenders': top_offenders,
        'avg_resolution_time': avg_resolution_time,
        'total_resolved': resolved_cases.count(),
    }
    return render(request, 'discipline/analytics.html', context)
