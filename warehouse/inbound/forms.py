from django import forms
from .models import FinalBayAssignment, GatehouseBooking, ProvisionalBayAssignment
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

class GatehouseBookingForm(forms.ModelForm):
    class Meta:
        model = GatehouseBooking
        fields = ['driver_name', 'company', 'vehicle_registration', 'trailer_number', 
                  'arrival_time', 'has_paperwork', 'paperwork_description', 'cancelled']
        widgets = {
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_registration': forms.TextInput(attrs={'class': 'form-control'}),
            'trailer_number': forms.TextInput(attrs={'class': 'form-control'}),
            'arrival_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'paperwork_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'has_paperwork': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cancelled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'driver_name': _('Driver Name'),
            'company': _('Company'),
            'vehicle_registration': _('Vehicle Registration'),
            'trailer_number': _('Trailer Number'),
            'arrival_time': _('Arrival Time'),
            'has_paperwork': _('Has Paperwork'),
            'paperwork_description': _('Paperwork Description'),
            'cancelled': _('Cancelled'),
        }
        help_texts = {
            'paperwork_description': _('Describe the paperwork if available.'),
        }

class ProvisionalBayAssignmentForm(forms.ModelForm):
    class Meta:
        model = ProvisionalBayAssignment
        fields = ['gatehouse_booking', 'provisional_bay', 'assigned_by', 'assigned_at']
        
class FinalBayAssignmentForm(forms.ModelForm):
    class Meta:
        model = FinalBayAssignment
        fields = ['provisional_bay_assignment', 'final_bay', 'confirmed_by', 'confirmed_at', 'is_loaded', 'loaded_at', 'loader']
        widgets = {
            'confirmed_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'loaded_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
