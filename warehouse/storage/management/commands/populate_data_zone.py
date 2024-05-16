# populate_zones.py

from django.core.management.base import BaseCommand
from warehouse.storage.models import Zone

class Command(BaseCommand):
    help = 'Populate data for Zone model'

    def handle(self, *args, **options):
        # Define the data to populate the Zone model
        zones_data = [
            {'name': 'Zone 1', 'description': 'Description for Zone 1'},
            {'name': 'Zone 2', 'description': 'Description for Zone 2'},
            {'name': 'Zone 3', 'description': 'Description for Zone 3'},
            {'name': 'Zone 4', 'description': 'Description for Zone 4'},
            # Add more zones as needed
        ]

        # Create Zone objects using the data
        for data in zones_data:
            Zone.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Successfully populated Zone model.'))






