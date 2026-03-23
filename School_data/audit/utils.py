from django.db import models
from datetime import date, datetime
from decimal import Decimal

def get_model_fields_dict(instance):
    fields_dict = {}
    from django.db.models.fields.files import FieldFile

    for field in instance._meta.fields:
        value = getattr(instance, field.name)
        if isinstance(value, (date, datetime)):
            value = value.isoformat()
        elif isinstance(value, Decimal):
            value = float(value)
        elif isinstance(value, models.Model):
            value = str(value)
        elif isinstance(value, (set, frozenset)):
            value = list(value)
        elif isinstance(value, FieldFile):
            value = value.name if value else None
        fields_dict[field.name] = value
    return fields_dict

def get_change_dict(old_data, new_data):
    changes = {}
    for key in new_data:
        old_val = old_data.get(key)
        new_val = new_data.get(key)
        if old_val != new_val:
            changes[key] = {'old': old_val, 'new': new_val}
    return changes

def get_audit_stats():
    from .models import AuditLog
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    last_24h = timezone.now() - timedelta(hours=24)
    return {
        'total_logs': AuditLog.objects.count(),
        'logs_24h': AuditLog.objects.filter(timestamp__gte=last_24h).count(),
        'actions_by_type': dict(AuditLog.objects.values('action').annotate(count=Count('action'))),
        'top_users': AuditLog.objects.values('user__username').annotate(count=Count('id')).order_by('-count')[:10],
    }
