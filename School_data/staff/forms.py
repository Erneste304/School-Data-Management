from django import forms
from accounts.models import CustomUser, StaffProfile

class StaffUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'photo', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['department', 'qualification', 'date_joined', 'notes']
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
