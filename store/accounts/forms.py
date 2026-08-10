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
        label='Email or username',
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'username',
                'placeholder': 'Email or username',
            },
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput()
    )

class OTPVerificationForm(forms.Form):
    """
    Validate the six-digit otp entered by the user.
    """

    code = forms.CharField(
        label='Verification code',
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'one-time-code',
                'inputmode': 'numeric',
            },
        ),
    )

    def clean_code(self):
        """Reject OTP input that contains non-numeric characters."""
        code = self.cleaned_data['code']

        if not code.isdigit():
            raise forms.ValidationError(
                'Enter the six-digit verification code.'
            )

        return code

class EmailEnrollmentForm(forms.Form):
    """Collect the email a legacy user must verify before future email logins."""

    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
                'placeholder': 'Email address',
            },
        ),
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
