from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from warehouse.inventory.models import User, Employee, Address

class EmployeeRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=255, required=True, help_text=_('Input first name'))
    last_name = forms.CharField(max_length=255, required=True, help_text=_('Input last name'))
    email = forms.EmailField(max_length=75, help_text=_('Enter a valid email address'))
    personal_email = forms.EmailField(max_length=75, help_text=_('Enter a valid personal email address'))
    dob = forms.DateField(help_text=_('Enter date of birth'))
    contact_number = forms.CharField(max_length=20, help_text=_('Enter at least 11+ numbers'))
    start_date = forms.DateField(help_text=_('Enter start date'))
    address = forms.ModelChoiceField(queryset=Address.objects.all(), help_text=_('Select your address'))
    position = forms.CharField(max_length=100, help_text=_('Enter your position'))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2',
                  'personal_email', 'dob', 'contact_number', 'start_date', 'address', 'position')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
            employee = Employee(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                dob=self.cleaned_data['dob'],
                personal_email=self.cleaned_data['personal_email'],
                contact_number=self.cleaned_data['contact_number'],
                address=self.cleaned_data['address'],
                position=self.cleaned_data['position'],
                start_date=self.cleaned_data['start_date'],
            )
            employee.save()
        return user