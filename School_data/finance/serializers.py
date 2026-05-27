from rest_framework import serializers
from .models import FeeCategory, FeeStructure, StudentFee, Payment, ExpenseCategory, Expense, Scholarship


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ['id', 'name', 'code', 'description', 'is_mandatory', 'is_recurring']


class FeeStructureSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = FeeStructure
        fields = ['id', 'academic_year', 'term', 'category', 'category_name',
                  'level', 'classroom', 'amount', 'frequency', 'due_date',
                  'late_fee', 'is_active']

    def get_category_name(self, obj):
        return obj.category.name


class StudentFeeSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StudentFee
        fields = ['id', 'student', 'fee_structure', 'academic_year', 'term',
                  'total_amount', 'amount_paid', 'balance', 'status',
                  'status_display', 'due_date', 'notes', 'student_name',
                  'category_name']
        read_only_fields = ['balance']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()

    def get_category_name(self, obj):
        return obj.fee_structure.category.name


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'receipt_number', 'student', 'student_fee', 'amount',
                  'payment_date', 'payment_method', 'method_display',
                  'reference_number', 'received_by', 'notes', 'created_at',
                  'student_name']
        read_only_fields = ['receipt_number', 'created_at']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'code', 'description', 'budget']


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = ['id', 'expense_number', 'category', 'category_name',
                  'description', 'amount', 'expense_date', 'paid_to',
                  'approved_by', 'recorded_by', 'notes', 'created_at']
        read_only_fields = ['expense_number', 'created_at']

    def get_category_name(self, obj):
        return obj.category.name


class ScholarshipSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Scholarship
        fields = ['id', 'student', 'type', 'type_display', 'percentage',
                  'amount', 'academic_year', 'reason', 'approved_by',
                  'start_date', 'end_date', 'is_active', 'student_name']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
