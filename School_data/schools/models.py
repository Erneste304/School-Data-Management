from django.db import models

LEVEL_CHOICES = (
    ('nursery', 'Nursery'),
    ('primary', 'Primary'),
    ('o_level', 'O-Level'),
    ('a_level', 'A-Level'),
)

class SchoolLevel(models.Model):
    name = models.CharField(max_length=20, choices=LEVEL_CHOICES, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_name_display()

class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True) # e.g., "2024"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

class Term(models.Model):
    TERM_CHOICES = (
        (1, 'Term 1'),
        (2, 'Term 2'),
        (3, 'Term 3'),
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    number = models.IntegerField(choices=TERM_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ['academic_year', 'number']
        ordering = ['academic_year', 'number']

    def __str__(self):
        return f"{self.academic_year.name} - Term {self.number}"

class Classroom(models.Model):
    name = models.CharField(max_length=50) # e.g., "Senior 1A", "PCB 1"
    level = models.ForeignKey(SchoolLevel, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    capacity = models.IntegerField(default=40)
    
    class Meta:
        unique_together = ['name', 'academic_year']

    def __str__(self):
        return f"{self.name} ({self.academic_year})"
