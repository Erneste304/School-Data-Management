from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.http import JsonResponse
from django.utils import timezone
from .models import (
    FeeCategory, FeeStructure, StudentFee, Payment,
    ExpenseCategory, Expense, FinancialSummary, Scholarship
)
from academics.models import Student
from schools.models import AcademicYear, Term, Classroom
from accounts.views import role_required
from .forms import (
    FeeStructureForm, StudentFeeForm, PaymentForm,
    ExpenseForm, ScholarshipForm, BulkFeeAssignmentForm
)

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def dashboard_view(request):
    """Finance dashboard for Accountant"""
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Financial summaries
    year_summary = FinancialSummary.objects.filter(
        academic_year=current_year, month__isnull=True
    ).first()
    if not year_summary and current_year:
        year_summary = FinancialSummary.objects.create(academic_year=current_year, month=None)
        year_summary.calculate_summary()
    
    # Current month summary
    current_month = timezone.now().month
    month_summary = FinancialSummary.objects.filter(
        academic_year=current_year, month=current_month
    ).first()
    if not month_summary and current_year:
        month_summary = FinancialSummary.objects.create(academic_year=current_year, month=current_month)
        month_summary.calculate_summary()
    
    # Pending fees
    pending_fees = StudentFee.objects.filter(
        academic_year=current_year,
        status__in=['pending', 'partial', 'overdue']
    )
    
    # Outstanding balance total
    outstanding_balance = pending_fees.aggregate(
        total=Sum('balance')
    )['total'] or 0
    
    # Recent transactions
    recent_payments = Payment.objects.select_related('student')[:10]
    recent_expenses = Expense.objects.select_related('category')[:10]
    
    # Income vs Expenses chart data
    last_6_months = []
    if current_year:
        for i in range(6):
            month = current_month - i
            if month < 1:
                month += 12
                year = current_year.start_date.year - 1
            else:
                year = current_year.start_date.year
                
            summary = FinancialSummary.objects.filter(
                academic_year__start_date__year=year,
                month=month
            ).first()
            
            if summary:
                last_6_months.append({
                    'month': month,
                    'income': float(summary.total_income),
                    'expenses': float(summary.total_expenses)
                })
    
    context = {
        'year_summary': year_summary,
        'month_summary': month_summary,
        'pending_fees_count': pending_fees.count(),
        'outstanding_balance': outstanding_balance,
        'recent_payments': recent_payments,
        'recent_expenses': recent_expenses,
        'chart_data': list(reversed(last_6_months)),
    }
    return render(request, 'finance/dashboard.html', context)

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def fee_structure_view(request):
    fee_structures = FeeStructure.objects.select_related('category', 'level', 'academic_year')
    academic_year_id = request.GET.get('academic_year')
    if academic_year_id:
        fee_structures = fee_structures.filter(academic_year_id=academic_year_id)
    context = {
        'fee_structures': fee_structures,
        'academic_years': AcademicYear.objects.all(),
        'selected_year': academic_year_id,
    }
    return render(request, 'finance/fee_structure.html', context)

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def add_fee_structure_view(request):
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            fee_structure = form.save()
            messages.success(request, f'Fee structure for {fee_structure.category.name} added successfully')
            return redirect('finance:fee_structure')
    else:
        form = FeeStructureForm()
    return render(request, 'finance/fee_structure_form.html', {'form': form})

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def student_fees_view(request):
    student_fees = StudentFee.objects.select_related('student', 'fee_structure__category')
    status = request.GET.get('status')
    if status:
        student_fees = student_fees.filter(status=status)
    classroom_id = request.GET.get('classroom')
    if classroom_id:
        student_fees = student_fees.filter(student__current_class_id=classroom_id)
    student_name = request.GET.get('student')
    if student_name:
        student_fees = student_fees.filter(student__user__first_name__icontains=student_name)
    context = {
        'student_fees': student_fees,
        'status_choices': StudentFee.STATUS_CHOICES,
        'classrooms': Classroom.objects.filter(academic_year__is_current=True),
        'filters': request.GET,
    }
    return render(request, 'finance/student_fees.html', context)

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def assign_fees_view(request):
    if request.method == 'POST':
        form = BulkFeeAssignmentForm(request.POST)
        if form.is_valid():
            fee_structure = form.cleaned_data['fee_structure']
            students = form.cleaned_data['students']
            assigned_count = 0
            for student in students:
                student_fee, created = StudentFee.objects.get_or_create(
                    student=student,
                    fee_structure=fee_structure,
                    defaults={
                        'academic_year': fee_structure.academic_year,
                        'term': fee_structure.term,
                        'total_amount': fee_structure.amount,
                        'due_date': fee_structure.due_date,
                    }
                )
                if created:
                    assigned_count += 1
            messages.success(request, f'Fees assigned to {assigned_count} students')
            return redirect('finance:student_fees')
    else:
        form = BulkFeeAssignmentForm()
    return render(request, 'finance/assign_fees.html', {'form': form})

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def record_payment_view(request):
    """Record a new payment"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.received_by = request.user
            payment.save()
            
            # Send email receipt (Fail silently in dev)
            from django.core.mail import send_mail
            from django.conf import settings
            try:
                receipt_data = {
                    'receipt_number': payment.receipt_number,
                    'student_name': payment.student.user.get_full_name(),
                    'amount': payment.amount,
                    'payment_date': payment.payment_date,
                    'payment_method': payment.get_payment_method_display(),
                    'reference': payment.reference_number,
                }
                subject = f'Payment Receipt - {payment.receipt_number}'
                msg = f"Dear Parent/Guardian,\n\nWe have received a payment of {payment.amount} for {receipt_data['student_name']}.\nReceipt: {payment.receipt_number}\nDate: {payment.payment_date}\nMethod: {payment.get_payment_method_display()}\n\nThank you."
                
                # Fetch student's parent email (fallback to student email)
                recipient = payment.student.user.email
                if hasattr(payment.student, 'parent') and payment.student.parent:
                    recipient = payment.student.parent.user.email
                
                if recipient:
                    send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)
            except Exception:
                pass
                
            messages.success(request, f'Payment of {payment.amount} recorded. Receipt: {payment.receipt_number}')
            return redirect('finance:payment_receipt', pk=payment.pk)
    else:
        # Pre-populate with selected student if provided
        student_id = request.GET.get('student')
        if student_id:
            student = get_object_or_404(Student, pk=student_id)
            form = PaymentForm(initial={'student': student})
        else:
            form = PaymentForm()
            
    return render(request, 'finance/record_payment.html', {'form': form})

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def payment_receipt_view(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'finance/payment_receipt.html', {'payment': payment})

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def expenses_view(request):
    expenses = Expense.objects.select_related('category')
    category_id = request.GET.get('category')
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    date_from = request.GET.get('date_from')
    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)
    date_to = request.GET.get('date_to')
    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)
    context = {
        'expenses': expenses,
        'categories': ExpenseCategory.objects.all(),
        'filters': request.GET,
    }
    return render(request, 'finance/expenses.html', context)

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def add_expense_view(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.recorded_by = request.user
            expense.save()
            messages.success(request, f'Expense {expense.expense_number} recorded')
            return redirect('finance:expenses')
    else:
        form = ExpenseForm()
    return render(request, 'finance/expense_form.html', {'form': form})

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def scholarships_view(request):
    scholarships = Scholarship.objects.select_related('student', 'approved_by')
    return render(request, 'finance/scholarships.html', {'scholarships': scholarships})

@login_required
@role_required(['head_teacher', 'admin'])
def add_scholarship_view(request):
    if request.method == 'POST':
        form = ScholarshipForm(request.POST)
        if form.is_valid():
            scholarship = form.save(commit=False)
            scholarship.approved_by = request.user
            scholarship.save()
            messages.success(request, f'Scholarship granted to {scholarship.student.user.get_full_name()}')
            return redirect('finance:scholarships')
    else:
        form = ScholarshipForm()
    return render(request, 'finance/scholarship_form.html', {'form': form})

@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def financial_report_view(request):
    academic_year_id = request.GET.get('academic_year')
    year_obj = get_object_or_404(AcademicYear, pk=academic_year_id) if academic_year_id else AcademicYear.objects.filter(is_current=True).first()
    monthly_summaries = FinancialSummary.objects.filter(academic_year=year_obj, month__isnull=False).order_by('month')
    total_payments_by_method = Payment.objects.filter(payment_date__year=year_obj.start_date.year).values('payment_method').annotate(total=Sum('amount'))
    total_expenses_by_category = Expense.objects.filter(expense_date__year=year_obj.start_date.year).values('category__name').annotate(total=Sum('amount'))
    context = {
        'year': year_obj,
        'monthly_summaries': monthly_summaries,
        'payments_by_method': total_payments_by_method,
        'expenses_by_category': total_expenses_by_category,
    }
@login_required
@role_required(['head_teacher', 'accountant', 'admin'])
def generate_financial_report(request):
    """Generate comprehensive financial report"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type', 'summary')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if not start_date or not end_date:
            messages.error(request, 'Please provide both start and end dates.')
            return redirect('finance:generate_report')
            
        payments = Payment.objects.filter(payment_date__range=[start_date, end_date])
        expenses = Expense.objects.filter(expense_date__range=[start_date, end_date])
        
        total_income = payments.aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        net_income = total_income - total_expenses
        
        payment_by_method = payments.values('payment_method').annotate(total=Sum('amount'))
        expense_by_category = expenses.values('category__name').annotate(total=Sum('amount'))
        
        outstanding = StudentFee.objects.filter(
            academic_year__is_current=True,
            status__in=['pending', 'partial', 'overdue']
        ).aggregate(total=Sum('balance'))['total'] or 0
        
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_income': net_income,
            'outstanding': outstanding,
            'payment_by_method': payment_by_method,
            'expense_by_category': expense_by_category,
            'payments': payments if report_type == 'detailed' else None,
            'expenses': expenses if report_type == 'detailed' else None,
        }
        
        # Returning HTML representation instead of PDF for now
        return render(request, 'finance/report_generated.html', context)
    
    return render(request, 'finance/generate_report.html')
