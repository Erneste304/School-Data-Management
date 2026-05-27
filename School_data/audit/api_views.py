from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import AuditLog, UserActivity
from .serializers import AuditLogSerializer, UserActivitySerializer
from .utils import get_audit_stats


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for audit logs — admins only."""
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        action = self.request.query_params.get('action')
        user_id = self.request.query_params.get('user_id')
        app = self.request.query_params.get('app')
        model = self.request.query_params.get('model')
        
        if action:
            qs = qs.filter(action=action)
        if user_id:
            qs = qs.filter(user_id=user_id)
        if app:
            qs = qs.filter(app_name=app)
        if model:
            qs = qs.filter(model_name=model)
        return qs[:200]  # Limit to latest 200


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivity.objects.select_related('user').all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset()[:100]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def audit_stats(request):
    """Return audit summary stats."""
    stats = get_audit_stats()
    # Convert querysets to serializable dicts
    stats['top_users'] = list(stats.get('top_users', []))
    return Response(stats)
