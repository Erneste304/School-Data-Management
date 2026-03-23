from django import forms
from .models import FeeStructure, StudentFee, Payment, Expense, Scholarship
from academics.models import Student
from schools.models import Classroom

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['academic_year', 'term', 'category', 'level', 'classroom', 'amount', 'frequency', 'due_date', 'late_fee']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'})}

class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee
        fields = ['student', 'fee_structure', 'total_amount', 'due_date']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'})}

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'student_fee', 'amount', 'payment_method', 'reference_number', 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_active=True)
        self.fields['student_fee'].queryset = StudentFee.objects.filter(status__in=['pending', 'partial', 'overdue'])

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'description', 'amount', 'expense_date', 'paid_to', 'receipt', 'notes']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship
        fields = ['student', 'type', 'percentage', 'academic_year', 'reason', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_active=True)

class BulkFeeAssignmentForm(forms.Form):
    fee_structure = forms.ModelChoiceField(queryset=FeeStructure.objects.filter(is_active=True))
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.filter(is_active=True), widget=forms.CheckboxSelectMultiple)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        classrooms = Classroom.objects.filter(academic_year__is_current=True)
        student_choices = []
        for classroom in classrooms:
            students = Student.objects.filter(current_class=classroom, is_active=True)
            if students.exists():
                student_choices.append((classroom.name, [(s.user.id, s.user.get_full_name()) for s in students]))
        self.fields['students'].choices = student_choices
