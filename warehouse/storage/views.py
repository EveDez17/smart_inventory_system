from django.shortcuts import render

from django.views.generic import TemplateView

from warehouse.storage.models import Location, SensorData

from django.utils import timezone

import datetime

class StorageDashboardView(TemplateView):
    template_name = 'storage_dashboard.html'

    def get_sensor_status_color(self, sensor_value):
        # Define your own thresholds and colors
        if sensor_value < 20:
            return 'green'  # Normal
        elif 20 <= sensor_value < 50:
            return 'yellow'  # Warning
        else:
            return 'red'  # Alert

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Assuming each location has a 'latest_sensor_data()' method that returns the most recent data
        locations_with_status = [
            {
                'code': location.code,
                'status_color': self.get_sensor_status_color(location.latest_sensor_data().value) 
                if location.latest_sensor_data() else 'grey',  # Grey if no sensor data available
            }
            for location in Location.objects.all()
        ]

        # Extracting data for the sensor data chart
        # This assumes you want to display data for the last 24 hours
        twenty_four_hours_ago = timezone.now() - datetime.timedelta(days=1)
        sensor_data = SensorData.objects.filter(timestamp__gte=twenty_four_hours_ago).order_by('timestamp')

        labels = [data.timestamp.strftime('%Y-%m-%d %H:%M') for data in sensor_data]
        values = [data.data for data in sensor_data]

        context['locations_with_status'] = locations_with_status
        context['labels'] = labels
        context['values'] = values
        return context




