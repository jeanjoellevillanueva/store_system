from django import forms
from django.contrib.auth.forms import AuthenticationForm


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
