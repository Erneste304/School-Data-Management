from django.core.management.base import BaseCommand
from django.apps import apps
from audit.models import AuditConfig

class Command(BaseCommand):
    help = 'Initializes AuditConfig for all models in the project'

    def handle(self, *args, **options):
        exclude_apps = ['admin', 'contenttypes', 'sessions', 'messages', 'staticfiles', 'audit']
        
        created_count = 0
        for model in apps.get_models():
            app_label = model._meta.app_label
            if app_label in exclude_apps:
                continue
                
            obj, created = AuditConfig.objects.get_or_create(
                model_name=model.__name__,
                app_name=app_label,
                defaults={
                    'enabled': True,
                    'track_creates': True,
                    'track_updates': True,
                    'track_deletes': True,
                }
            )
            if created:
                created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully initialized {created_count} audit configurations'))
