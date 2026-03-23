from django import forms
from .models import DisciplineCase, DisciplineAction, DisciplineHearing, IncidentReport
from academics.models import Student

class DisciplineCaseForm(forms.ModelForm):
    class Meta:
        model = DisciplineCase
        fields = [
            'student', 'category', 'incident_date', 'incident_location',
            'description', 'evidence', 'status', 'assigned_to'
        ]
        widgets = {
            'incident_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_active=True)
        self.fields['assigned_to'].queryset = self.fields['assigned_to'].queryset.filter(role='dod')

class DisciplineActionForm(forms.ModelForm):
    class Meta:
        model = DisciplineAction
        fields = ['action_type', 'description', 'due_date', 'notes']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class HearingForm(forms.ModelForm):
    committee_members = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = DisciplineHearing
        fields = [
            'hearing_date', 'venue', 'chairperson', 'committee_members',
            'parent_present', 'parent_name', 'parent_comment',
            'student_statement', 'findings', 'recommendations', 'decision'
        ]
        widgets = {
            'hearing_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'parent_comment': forms.Textarea(attrs={'rows': 3}),
            'student_statement': forms.Textarea(attrs={'rows': 3}),
            'findings': forms.Textarea(attrs={'rows': 4}),
            'recommendations': forms.Textarea(attrs={'rows': 3}),
            'decision': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import CustomUser
        self.fields['chairperson'].queryset = CustomUser.objects.filter(
            role__in=['head_teacher', 'dod', 'admin']
        )
        self.fields['committee_members'].queryset = CustomUser.objects.filter(
            role__in=['head_teacher', 'dod', 'teacher', 'admin']
        )

class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = ['title', 'report_date', 'period', 'cases_included', 'summary', 'recommendations']
        widgets = {
            'report_date': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 5}),
            'recommendations': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cases_included'].queryset = DisciplineCase.objects.filter(
            status__in=['resolved', 'closed']
        )
