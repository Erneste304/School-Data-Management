from django.contrib import admin
from .models import (
    FeeCategory, FeeStructure, StudentFee, Payment,
    ExpenseCategory, Expense, FinancialSummary, Scholarship
)

class StudentFeeInline(admin.TabularInline):
    model = StudentFee
    extra = 1
    fields = ['fee_structure', 'total_amount', 'amount_paid', 'status', 'due_date']

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    fields = ['receipt_number', 'amount', 'payment_method', 'payment_date']

class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'total_amount', 'amount_paid', 'balance', 'status']
    list_filter = ['status', 'academic_year', 'due_date']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__student_id']
    inlines = [PaymentInline]
    readonly_fields = ['balance']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'student', 'amount', 'payment_date', 'payment_method', 'received_by']
    list_filter = ['payment_method', 'payment_date', 'received_by']
    search_fields = ['receipt_number', 'student__user__first_name', 'reference_number']
    readonly_fields = ['receipt_number']

class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['category', 'level', 'amount', 'academic_year', 'due_date', 'is_active']
    list_filter = ['academic_year', 'category', 'level', 'is_active']

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['expense_number', 'category', 'description', 'amount', 'expense_date']
    list_filter = ['category', 'expense_date']
    search_fields = ['expense_number', 'description']

class FinancialSummaryAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'month', 'total_income', 'total_expenses', 'net_balance']
    list_filter = ['academic_year']
    readonly_fields = ['total_income', 'total_expenses', 'net_balance', 'expected_income']

class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ['student', 'type', 'percentage', 'academic_year', 'is_active']
    list_filter = ['type', 'academic_year', 'is_active']
    search_fields = ['student__user__first_name']

admin.site.register(FeeCategory)
admin.site.register(FeeStructure, FeeStructureAdmin)
admin.site.register(StudentFee, StudentFeeAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(ExpenseCategory)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(FinancialSummary, FinancialSummaryAdmin)
admin.site.register(Scholarship, ScholarshipAdmin)
