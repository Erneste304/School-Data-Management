from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q

from .models import DisciplineCategory, DisciplineCase, DisciplineAction
from .serializers import (
    DisciplineCategorySerializer, DisciplineCaseSerializer,
    DisciplineActionSerializer
)


class DisciplineCategoryViewSet(viewsets.ModelViewSet):
    queryset = DisciplineCategory.objects.all()
    serializer_class = DisciplineCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class DisciplineCaseViewSet(viewsets.ModelViewSet):
    queryset = DisciplineCase.objects.select_related(
        'student__user', 'reported_by', 'category'
    ).prefetch_related('actions').all()
    serializer_class = DisciplineCaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        student_id = self.request.query_params.get('student_id')
        severity = self.request.query_params.get('severity')

        if status_param:
            qs = qs.filter(status=status_param)
        if student_id:
            qs = qs.filter(student__user_id=student_id)
        if severity:
            qs = qs.filter(category__severity=severity)
        return qs

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


class DisciplineActionViewSet(viewsets.ModelViewSet):
    queryset = DisciplineAction.objects.select_related('case', 'taken_by').all()
    serializer_class = DisciplineActionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        case_id = self.request.query_params.get('case_id')
        if case_id:
            qs = qs.filter(case_id=case_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(taken_by=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def discipline_summary(request):
    """Return discipline dashboard stats."""
    total_cases = DisciplineCase.objects.count()
    open_cases = DisciplineCase.objects.filter(
        status__in=['reported', 'investigating']
    ).count()
    resolved_cases = DisciplineCase.objects.filter(
        status__in=['resolved', 'closed']
    ).count()

    by_severity = {}
    for case in DisciplineCase.objects.select_related('category').all():
        sev = case.category.get_severity_display() if case.category else 'Unknown'
        by_severity[sev] = by_severity.get(sev, 0) + 1

    return Response({
        'total_cases': total_cases,
        'open_cases': open_cases,
        'resolved_cases': resolved_cases,
        'by_severity': by_severity,
    })
