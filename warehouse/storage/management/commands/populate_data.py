# populate_aisles.py

from django.core.management.base import BaseCommand
from warehouse.storage.models import Zone, Aisle

class Command(BaseCommand):
    help = 'Populate data for Aisle model'

    def handle(self, *args, **options):
        # Get all zones
        zones = Zone.objects.all()

        # Define the number of aisles per zone
        aisles_per_zone = 5

        # Define aisle letters for each zone
        zone_aisle_letters = {
            1: ['M', 'T', 'X', 'D', 'E'],
            2: ['F', 'G', 'H', 'I', 'J'],
            # Add more zones as needed
        }

        # Populate aisles for each zone
        for zone in zones:
            aisle_letters = zone_aisle_letters.get(zone.id)
            if aisle_letters:
                for aisle_letter in aisle_letters:
                    aisle_data = {
                        'zone': zone,
                        'aisle_letter': aisle_letter,
                    }
                    Aisle.objects.create(**aisle_data)
            else:
                self.stdout.write(self.style.WARNING(f'No aisle letters defined for Zone {zone.id}.'))

        self.stdout.write(self.style.SUCCESS('Successfully populated Aisle model.'))
