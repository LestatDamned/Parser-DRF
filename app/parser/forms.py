from django import forms
from django.contrib.auth.models import User

from parser.models import HistorySearch


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "confirm_password": forms.PasswordInput(attrs={"class": "form-control"}),
        }


class ParsingForm(forms.ModelForm):
    class Meta:
        model = HistorySearch
        fields = ("searching_key", "searching_filter", "parsing_options")
        widgets = {
            "searching_key": forms.TextInput(attrs={"class": "form-control"}),
            "searching_filter": forms.Select(attrs={"class": "form-control"}),
            "parsing_options": forms.Select(attrs={"class": "form-control"}),

        }


class AuthorizationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
        }
