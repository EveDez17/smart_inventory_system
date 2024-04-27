from django.core.management.base import BaseCommand
from warehouse.inventory.models import StockLevel, FoodProduct
from warehouse.storage.models import Location, PickFace, Rack, Level
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create stock levels for testing'

    def handle(self, *args, **kwargs):
        # Define location attributes
        location_code = "D011"
        rack_number = 5
        aisle_id = 3
        level_number = '2'

        # Check if location with the specified code already exists
        existing_location = Location.objects.filter(code=location_code).first()
        if existing_location:
            self.stdout.write(self.style.WARNING(f"Location with code {location_code} already exists. Skipping creation."))
            return

        # Create a rack if it doesn't exist
        rack, _ = Rack.objects.get_or_create(rack_number=rack_number, aisle_id=aisle_id)

        # Create a level if it doesn't exist
        level, _ = Level.objects.get_or_create(rack=rack, level=level_number)

        # Create a location
        location = Location.objects.create(
            code=location_code,
            level=level,
            side="W",
            location_number=1,
            weight=100,  # Set weight to non-zero value
            status='full'  # Set status accordingly
        )

        # Create some food products
        product1 = FoodProduct.objects.create(
            name="Product Frozen",
            sku="SKU001",
            unit_price=10.0,
            category="2",
            batch_number="BATCH001",
            storage_temperature="Temperature A",
            date_received=timezone.now(),
            expiration_date=timezone.now() + timedelta(days=30),
            supplier="Supplier A",
            last_updated_by="Admin"
        )
        product2 = FoodProduct.objects.create(
            name="Product B",
            sku="SKU002",
            unit_price=15.0,
            category="3",
            batch_number="BATCH002",
            storage_temperature="Temperature B",
            date_received=timezone.now(),
            expiration_date=timezone.now() + timedelta(days=60),
            supplier="Supplier B",
            last_updated_by="Admin"
        )

        # Create some pick faces
        pick_face1 = PickFace.objects.create(location=location, pick_face_code="PF008", product=product1, category=None)
        pick_face2 = PickFace.objects.create(location=location, pick_face_code="PF010", product=product2, category=None)

        # Create stock levels with non-zero quantity
        StockLevel.objects.create(location=location, pick_face=pick_face1, product=product1, quantity=100,
                                  expiration_date=timezone.now() + timedelta(days=30))
        StockLevel.objects.create(location=location, pick_face=pick_face2, product=product2, quantity=200,
                                  expiration_date=timezone.now() + timedelta(days=60))
        StockLevel.objects.create(location=location, pick_face=pick_face2, product=product1, quantity=150,
                                  expiration_date=timezone.now() - timedelta(days=10))

        self.stdout.write(self.style.SUCCESS('Stock levels created successfully'))







