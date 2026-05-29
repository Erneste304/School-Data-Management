from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, StaffProfile, ParentProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class StaffCreateForm(forms.ModelForm):
    """Used by Head Teacher and Admin to create new staff accounts."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'role', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control'}),
            'role':       forms.Select(attrs={'class': 'form-control'}),
            'photo':      forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Head teacher cannot create admin accounts — only admin can
        requesting_user = kwargs.pop('requesting_user', None)
        super().__init__(*args, **kwargs)
        if requesting_user and not requesting_user.is_admin:
            # Remove 'admin' from role choices for non-admin creators
            self.fields['role'].choices = [
                (v, l) for v, l in CustomUser.Role.choices if v != 'admin'
            ]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class StaffEditForm(forms.ModelForm):
    """Edit existing staff — no password change here (separate view for that)."""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'role', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control'}),
            'role':       forms.Select(attrs={'class': 'form-control'}),
            'photo':      forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        requesting_user = kwargs.pop('requesting_user', None)
        super().__init__(*args, **kwargs)
        if requesting_user and not requesting_user.is_admin:
            self.fields['role'].choices = [
                (v, l) for v, l in CustomUser.Role.choices if v != 'admin'
            ]


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['department', 'qualification', 'date_joined', 'notes']
        widgets = {
            'department':    forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'date_joined':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StudentCreateForm(forms.ModelForm):
    """Used by Admin and Head Teacher to create new student accounts."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    student_id = forms.CharField(
        label='Student ID',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Unique student identifier (e.g., STU0001)'
    )
    enrollment_date = forms.DateField(
        label='Enrollment Date',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    current_class = forms.ModelChoiceField(
        label='Class',
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Assign student to a class (optional)'
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control'}),
            'photo':      forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from academics.models import Class
        self.fields['current_class'].queryset = Class.objects.all()

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = CustomUser.Role.STUDENT
        if commit:
            user.save()
        return user


class ParentCreateForm(forms.ModelForm):
    """Used by Admin and Head Teacher to create new parent accounts."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    occupation = forms.CharField(
        label='Occupation',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    workplace = forms.CharField(
        label='Workplace',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    emergency_contact = forms.CharField(
        label='Emergency Contact',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control'}),
            'photo':      forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = CustomUser.Role.PARENT
        if commit:
            user.save()
        return user


class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ['occupation', 'workplace', 'emergency_contact', 'relationship_to_student', 'notes']
        widgets = {
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'workplace': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship_to_student': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ParentStudentLinkForm(forms.Form):
    """Form to link a parent to one or more students."""
    parent = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='parent'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Parent'
    )
    students = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='student'),
        widget=forms.CheckboxSelectMultiple,
        label='Students',
        required=True
    )
    relationship_type = forms.ChoiceField(
        choices=[
            ('Father', 'Father'),
            ('Mother', 'Mother'),
            ('Guardian', 'Guardian'),
            ('Step-parent', 'Step-parent'),
            ('Other', 'Other'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Relationship Type'
    )
    is_primary_guardian = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Primary Guardian'
    )
    can_view_grades = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can View Grades'
    )
    can_view_attendance = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can View Attendance'
    )
    can_view_discipline = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can View Discipline'
    )
    can_view_fees = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can View Fees'
    )


class UserProfileForm(forms.ModelForm):
    """Form for users to edit their own profile information."""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class UserPasswordChangeForm(forms.Form):
    """Form for users to change their password."""
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        return current_password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('New passwords do not match.')
        return cleaned

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user