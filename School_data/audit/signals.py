from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import sys
from .models import AuditLog, AuditConfig
from .utils import get_change_dict, get_model_fields_dict

def is_migration():
    return any(arg in sys.argv for arg in ['migrate', 'makemigrations', 'init_audit_config'])

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if is_migration(): return
    if not hasattr(instance, '_audit_old_data'):
        if instance.pk:
            try:
                old_instance = sender.objects.get(pk=instance.pk)
                instance._audit_old_data = get_model_fields_dict(old_instance)
            except sender.DoesNotExist:
                instance._audit_old_data = {}
        else:
            instance._audit_old_data = {}

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if is_migration(): return
    config = get_audit_config(sender)
    if not config or not config.enabled:
        return
    
    if created and config.track_creates:
        action = 'create'
        old_data = {}
        new_data = get_model_fields_dict(instance)
    elif not created and config.track_updates:
        action = 'update'
        old_data = getattr(instance, '_audit_old_data', {})
        new_data = get_model_fields_dict(instance)
        if config.exclude_fields:
            for field in config.exclude_fields:
                old_data.pop(field, None)
                new_data.pop(field, None)
        if old_data == new_data:
            return
    else:
        return
    
    user = get_current_user()
    
    AuditLog.objects.create(
        action=action,
        user=user,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=str(instance.pk),
        object_repr=str(instance),
        model_name=sender.__name__,
        app_name=sender._meta.app_label,
        old_data=old_data,
        new_data=new_data,
        changes=get_change_dict(old_data, new_data),
        user_ip=get_request_ip(),
        user_agent=get_user_agent(),
        request_path=get_request_path(),
        request_method=get_request_method(),
    )

@receiver(pre_delete)
def audit_pre_delete(sender, instance, **kwargs):
    if is_migration(): return
    if instance.pk:
        instance._audit_delete_data = get_model_fields_dict(instance)

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if is_migration(): return
    config = get_audit_config(sender)
    if not config or not config.enabled or not config.track_deletes:
        return
    
    AuditLog.objects.create(
        action='delete',
        user=get_current_user(),
        content_type=ContentType.objects.get_for_model(instance),
        object_id=str(instance.pk),
        object_repr=str(instance),
        model_name=sender.__name__,
        app_name=sender._meta.app_label,
        old_data=getattr(instance, '_audit_delete_data', {}),
        new_data={},
        changes={},
        user_ip=get_request_ip(),
        user_agent=get_user_agent(),
        request_path=get_request_path(),
        request_method=get_request_method(),
    )

def get_audit_config(model):
    try:
        return AuditConfig.objects.get(model_name=model.__name__, app_name=model._meta.app_label)
    except Exception:
        return None

def get_current_user():
    from .thread_local import get_current_request
    request = get_current_request()
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None

def get_request_ip():
    from .thread_local import get_current_request
    request = get_current_request()
    return getattr(request, '_audit_ip', None)

def get_user_agent():
    from .thread_local import get_current_request
    request = get_current_request()
    return getattr(request, '_audit_user_agent', '')

def get_request_path():
    from .thread_local import get_current_request
    request = get_current_request()
    return getattr(request, '_audit_path', '')

def get_request_method():
    from .thread_local import get_current_request
    request = get_current_request()
    return getattr(request, '_audit_method', '')
