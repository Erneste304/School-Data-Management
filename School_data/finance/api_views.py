from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import (
    FeeCategory, FeeStructure, StudentFee, Payment,
    ExpenseCategory, Expense, Scholarship
)
from .serializers import (
    FeeCategorySerializer, FeeStructureSerializer, StudentFeeSerializer,
    PaymentSerializer, ExpenseCategorySerializer, ExpenseSerializer,
    ScholarshipSerializer
)


class FeeCategoryViewSet(viewsets.ModelViewSet):
    queryset = FeeCategory.objects.all()
    serializer_class = FeeCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related('category').filter(is_active=True)
    serializer_class = FeeStructureSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentFeeViewSet(viewsets.ModelViewSet):
    queryset = StudentFee.objects.select_related(
        'student__user', 'fee_structure__category'
    ).all()
    serializer_class = StudentFeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Students/parents only see their own fees
        if user.role == 'student':
            qs = qs.filter(student__user=user)
        elif user.role == 'parent':
            from accounts.models import ParentStudentRelationship
            child_ids = ParentStudentRelationship.objects.filter(
                parent__user=user, can_view_fees=True
            ).values_list('student_id', flat=True)
            qs = qs.filter(student_id__in=child_ids)

        student_id = self.request.query_params.get('student_id')
        fee_status = self.request.query_params.get('status')
        if student_id:
            qs = qs.filter(student__user_id=student_id)
        if fee_status:
            qs = qs.filter(status=fee_status)
        return qs


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('student__user').all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'student':
            qs = qs.filter(student__user=user)

        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student__user_id=student_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related('category').all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.select_related('student__user').filter(is_active=True)
    serializer_class = ScholarshipSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def finance_summary(request):
    """Return financial dashboard summary stats."""
    today = timezone.now().date()

    total_expected = StudentFee.objects.aggregate(
        total=Sum('total_amount'))['total'] or 0
    total_collected = StudentFee.objects.aggregate(
        total=Sum('amount_paid'))['total'] or 0
    total_balance = StudentFee.objects.aggregate(
        total=Sum('balance'))['total'] or 0
    total_expenses = Expense.objects.aggregate(
        total=Sum('amount'))['total'] or 0

    fee_status_counts = dict(
        StudentFee.objects.values('status').annotate(
            count=Count('id')
        ).values_list('status', 'count')
    )

    recent_payments = PaymentSerializer(
        Payment.objects.select_related('student__user').order_by('-created_at')[:5],
        many=True
    ).data

    return Response({
        'total_expected': float(total_expected),
        'total_collected': float(total_collected),
        'total_balance': float(total_balance),
        'total_expenses': float(total_expenses),
        'net_income': float(total_collected) - float(total_expenses),
        'collection_rate': round(
            (float(total_collected) / float(total_expected) * 100) if total_expected else 0, 1
        ),
        'fee_status_counts': fee_status_counts,
        'recent_payments': recent_payments,
    })
