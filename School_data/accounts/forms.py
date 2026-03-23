from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, StaffProfile


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