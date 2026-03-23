from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import CustomUser
from academics.models import Student
from schools.models import AcademicYear, Term, Classroom, SchoolLevel

class FeeCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    is_recurring = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Fee Categories"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class FeeStructure(models.Model):
    FREQUENCY_CHOICES = (
        ('termly', 'Per Term'),
        ('yearly', 'Per Year'),
        ('monthly', 'Per Month'),
        ('one_time', 'One Time'),
    )
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    level = models.ForeignKey(SchoolLevel, on_delete=models.CASCADE, null=True, blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='termly')
    due_date = models.DateField()
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['academic_year', 'level', 'category']
        unique_together = ['academic_year', 'category', 'level', 'term']
    
    def __str__(self):
        return f"{self.category.name} - {self.level} - {self.amount} ({self.academic_year})"

class StudentFee(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-due_date', 'student']
        unique_together = ['student', 'fee_structure']
    
    def save(self, *args, **kwargs):
        self.balance = self.total_amount - self.amount_paid
        if self.balance <= 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        elif self.due_date < timezone.now().date() and self.balance > 0:
            self.status = 'overdue'
        else:
            self.status = 'pending'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.fee_structure.category.name}: {self.status}"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
        ('online', 'Online Payment'),
    )
    
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=100, blank=True)
    received_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='received_payments')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            import random
            year = timezone.now().year
            month = timezone.now().month
            self.receipt_number = f"RCPT{year}{month:02d}{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)
        
        if self.student_fee:
            self.student_fee.amount_paid += self.amount
            self.student_fee.save()
    
    def __str__(self):
        return f"{self.receipt_number} - {self.student.user.get_full_name()} - {self.amount}"

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Expense(models.Model):
    expense_number = models.CharField(max_length=50, unique=True, blank=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(default=timezone.now)
    paid_to = models.CharField(max_length=200)
    receipt = models.FileField(upload_to='expense_receipts/', blank=True, null=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_expenses')
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='recorded_expenses')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expense_number:
            import random
            year = timezone.now().year
            self.expense_number = f"EXP{year}{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.expense_number} - {self.category.name} - {self.amount}"

class FinancialSummary(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    month = models.IntegerField(null=True, blank=True)
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    collected_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    generated_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['academic_year', 'month']
        ordering = ['-academic_year', '-month']
    
    def calculate_summary(self):
        payments = Payment.objects.filter(payment_date__year=self.academic_year.start_date.year)
        if self.month:
            payments = payments.filter(payment_date__month=self.month)
        
        self.total_income = payments.aggregate(total=models.Sum('amount'))['total'] or 0
        
        expenses = Expense.objects.filter(expense_date__year=self.academic_year.start_date.year)
        if self.month:
            expenses = expenses.filter(expense_date__month=self.month)
        
        self.total_expenses = expenses.aggregate(total=models.Sum('amount'))['total'] or 0
        
        expected_fees = StudentFee.objects.filter(
            academic_year=self.academic_year,
            status__in=['pending', 'partial', 'overdue']
        )
        if self.month:
            expected_fees = expected_fees.filter(due_date__month=self.month)
        
        self.expected_income = expected_fees.aggregate(total=models.Sum('balance'))['total'] or 0
        self.collected_income = payments.aggregate(total=models.Sum('amount'))['total'] or 0
        self.net_balance = self.total_income - self.total_expenses
        
        self.save()
    
    def __str__(self):
        if self.month:
            return f"{self.academic_year} - Month {self.month}"
        return f"{self.academic_year} - Annual Summary"

class Scholarship(models.Model):
    SCHOLARSHIP_TYPES = (
        ('academic', 'Academic Merit'),
        ('sports', 'Sports'),
        ('need_based', 'Financial Need'),
        ('special', 'Special Consideration'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scholarships')
    type = models.CharField(max_length=20, choices=SCHOLARSHIP_TYPES)
    percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    reason = models.TextField()
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def save(self, *args, **kwargs):
        if not self.amount and self.percentage:
            from django.db.models import Sum
            total_fees = StudentFee.objects.filter(
                student=self.student,
                academic_year=self.academic_year
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            self.amount = (self.percentage / 100) * total_fees
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.percentage}% {self.type}"
