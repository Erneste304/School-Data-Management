from django import forms
from .models import Class, Subject, Student, Enrollment
from Users.models import CustomUser

class ClassForm(forms.ModelForm):
    """Form for creating and editing academic classes."""
    class Meta:
        model = Class
        fields = ['name', 'class_tutor']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict class tutor choices to only TEACHER and HEAD roles
        self.fields['class_tutor'].queryset = CustomUser.objects.filter(
            profile__role__in=['TEACHER', 'HEAD']
        )

class SubjectForm(forms.ModelForm):
    """Form for creating and editing subjects."""
    class Meta:
        model = Subject
        fields = ['name', 'code', 'teacher']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict teacher choices to only TEACHER role
        self.fields['teacher'].queryset = CustomUser.objects.filter(
            profile__role='TEACHER'
        )
        
class StudentUpdateForm(forms.ModelForm):
    """
    Form to update the academic record for an existing Student.
    The 'user' field is made read-only as it should not be changed after creation.
    """
    class Meta:
        model = Student
        fields = ['user', 'student_id', 'current_class', 'is_active']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the user field read-only on the form
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['user'].disabled = True