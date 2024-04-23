from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Employee

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_approved = forms.BooleanField(required=False, initial=False, label=_("Approve User"))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2', 'is_approved')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomUserChangeForm(UserChangeForm):
    first_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_approved = forms.BooleanField(required=False, label=_("Approve User"))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'is_approved', 'password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EmployeeRegistrationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))  # Assuming email is here for simplicity

    class Meta:
        model = Employee
        fields = ('employee_first_name', 'employee_last_name', 'employee_street_number', 'employee_street_name',
                  'employee_city', 'employee_county', 'employee_country', 'employee_post_code', 'date_hired', 'role', 'email')
        widgets = {
            'employee_first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_street_number': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_street_name': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_city': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_county': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_country': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_post_code': forms.TextInput(attrs={'class': 'form-control'}),
            'date_hired': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),  # Managed here for simplicity
        }