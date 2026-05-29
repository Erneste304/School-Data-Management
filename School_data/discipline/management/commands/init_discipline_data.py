from django.core.management.base import BaseCommand
from discipline.models import DisciplineCategory


class Command(BaseCommand):
    help = 'Initialize default discipline categories'

    def handle(self, *args, **options):
        if DisciplineCategory.objects.count() == 0:
            categories = [
                {
                    'name': 'Late Arrival',
                    'description': 'Student arrives late to class or school',
                    'severity': 'minor',
                    'default_action': 'Verbal Warning',
                    'points': 1
                },
                {
                    'name': 'Uniform Violation',
                    'description': 'Not wearing proper school uniform',
                    'severity': 'minor',
                    'default_action': 'Warning',
                    'points': 1
                },
                {
                    'name': 'Disruptive Behavior',
                    'description': 'Disrupting class or school activities',
                    'severity': 'moderate',
                    'default_action': 'Written Warning',
                    'points': 3
                },
                {
                    'name': 'Incomplete Homework',
                    'description': 'Repeated failure to complete homework assignments',
                    'severity': 'moderate',
                    'default_action': 'Parent Meeting',
                    'points': 2
                },
                {
                    'name': 'Bullying',
                    'description': 'Bullying or harassing other students',
                    'severity': 'major',
                    'default_action': 'Suspension',
                    'points': 10
                },
                {
                    'name': 'Fighting',
                    'description': 'Physical altercation with other students',
                    'severity': 'major',
                    'default_action': 'Suspension',
                    'points': 15
                },
                {
                    'name': 'Vandalism',
                    'description': 'Damaging school property',
                    'severity': 'major',
                    'default_action': 'Community Service',
                    'points': 20
                },
                {
                    'name': 'Theft',
                    'description': 'Stealing school or personal property',
                    'severity': 'critical',
                    'default_action': 'Suspension',
                    'points': 25
                },
                {
                    'name': 'Drug/Alcohol Possession',
                    'description': 'Possession or use of illegal substances',
                    'severity': 'critical',
                    'default_action': 'Expulsion',
                    'points': 50
                },
                {
                    'name': 'Weapon Possession',
                    'description': 'Possession of weapons on school premises',
                    'severity': 'critical',
                    'default_action': 'Expulsion',
                    'points': 50
                },
            ]
            
            for cat_data in categories:
                DisciplineCategory.objects.create(**cat_data)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(categories)} discipline categories'))
        else:
            self.stdout.write(self.style.WARNING('Discipline categories already exist'))
