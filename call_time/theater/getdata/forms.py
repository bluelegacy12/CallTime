from django import forms
from .models import Performers
from django.contrib.auth.models import User

class NameForm(forms.ModelForm):
    name = forms.CharField(label="Name", max_length=128)
    password = forms.CharField(widget=forms.PasswordInput)
    retype_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    retype_password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=128)
    last_name = forms.CharField(max_length=128)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

class AddPerformerForm(forms.ModelForm):
    company = forms.CharField(max_length=128)
    class Meta:
        model = User
        fields = ['company', 'email']

class AddStaffForm(forms.ModelForm):
    first_name = forms.CharField(max_length=128)
    last_name = forms.CharField(max_length=128)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
