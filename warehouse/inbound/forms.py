from django import forms
from .models import GatehouseBooking
# Gatehouse Bookin
class GatehouseBookingForm(forms.ModelForm):
    class Meta:
        model = GatehouseBooking
        fields = ['driver_name', 'company', 'vehicle_registration', 'trailer_number', 'arrival_time', 'has_paperwork', 'paperwork_description']
        widgets = {
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super(GatehouseBookingForm, self).__init__(*args, **kwargs)
        self.fields['arrival_time'].input_formats = ('%Y-%m-%dT%H:%M',)
        
        
# Search


class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=100, required=False, label='Search')

class GatehouseBookingForm(forms.ModelForm):
    class Meta:
        model = GatehouseBooking
        fields = ['driver_name', 'company', 'vehicle_registration', 'trailer_number', 'arrival_time']

