from django import forms
from .models import GatehouseBooking

class GatehouseBookingForm(forms.ModelForm):
    class Meta:
        model = GatehouseBooking
        fields = ['driver_name', 'company', 'vehicle_registration', 'trailer_number', 'arrival_time', 'paperwork']
        widgets = {
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super(GatehouseBookingForm, self).__init__(*args, **kwargs)
        self.fields['arrival_time'].input_formats = ('%Y-%m-%dT%H:%M',)
