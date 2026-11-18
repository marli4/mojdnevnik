from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "patronimic",
            "role",
            "group",
        )

class MyLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Логин"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Пароль"}))