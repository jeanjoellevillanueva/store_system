from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

from .models import Employee


class LoginForm(AuthenticationForm):
    """
    Form used for logging in.
    """
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput()
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput()
    )


class EmployeeForm(forms.ModelForm):
    """
    Forms for Employee Model.
    """
    class Meta:
        model = Employee
        fields = ['base_pay', 'designation', 'department']


class UserForm(forms.ModelForm):
    """
    Forms for User Model.
    """
    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser'
        ]


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.instance and self.instance.username == username:
            return username
        elif User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
