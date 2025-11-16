from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile, ROLE_CHOICES
from Academics.models import Student

class UserProfileCreationForm(UserCreationForm):
     
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    
    student_id = forms.CharField(max_length=20, required=False, help_text="Required if role is 'Student'")
    enrollment_date = forms.DateField(required=False, help_text="Required if role is 'Student'")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

    @transaction.atomic
    def save(self, commit=True):
        """
        Overrides save to ensure both the CustomUser and the Profile are created.
        """
        user = super().save(commit=False)

        if commit:
            user.save()
            role = self.cleaned_data.get('role')
            Profile.objects.create(user=user, role=role)

            # If the role is 'STUDENT', also create the Student academic record
            if role == 'STUDENT':
                student_id = self.cleaned_data.get('student_id')
                enrollment_date = self.cleaned_data.get('enrollment_date')
                Student.objects.create(user=user, student_id=student_id, enrollment_date=enrollment_date)

        return user