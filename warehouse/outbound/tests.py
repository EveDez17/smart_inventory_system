from django.test import TestCase
from django.contrib.auth import get_user_model

from warehouse.storage.models import Aisle, Level, Rack, Zone
from .models import Outbound

User = get_user_model()

class OutboundModelTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='manager', email='manager@example.com', password='testpass123')

        # Ensure the user has been created successfully
        assert self.user is not None, "User creation failed."

        # Create dependent objects
        self.zone = Zone.objects.create(name='Storage Zone', description='Zone description')
        self.aisle = Aisle.objects.create(zone=self.zone, aisle_letter='A')
        self.rack = Rack.objects.create(aisle=self.aisle, rack_number='R1')
        self.level = Level.objects.create(rack=self.rack, level='G')

        # Ensure all objects are created
        assert self.zone and self.aisle and self.rack and self.level, "Dependent object creation failed."

        # Create the Outbound object
        self.outbound = Outbound.objects.create(
            address='1234 Warehouse Drive',
            floor_number=1,
            bay_number=1,
            additional_info='Details about the location',
            location_identifier='WH-123',
            max_capacity=100,
            operational_restrictions='None',
            special_handling_required=False,
            outbound_code='OUT123',
            managing_user=self.user,
            utilized_capacity=50,
            code='A0123',  # Make sure this field is filled as it's required
            level=self.level,
            side='N',
            location_number=1
        )

    def test_string_representation(self):
        expected_str = "OUT123 - Floor 1 - Bay 1"
        self.assertEqual(str(self.outbound), expected_str)

    def test_get_default_location(self):
        # This test checks if the get_default_location method creates a default location
        default_location = Outbound.get_default_location()
        self.assertIsNotNone(default_location)
        self.assertEqual(default_location.outbound_code, 'A0045')
        self.assertEqual(default_location.location_identifier, 'DEFAULT_OUTBOUND')

        # Optionally, check for defaults set in the method
        self.assertEqual(default_location.address, 'Default Address')
        self.assertEqual(default_location.floor_number, 1)
        self.assertEqual(default_location.bay_number, 1)
        self.assertEqual(default_location.additional_info, 'Default outbound location')
        self.assertEqual(default_location.max_capacity, 1000)
        self.assertEqual(default_location.operational_restrictions, 'None')
        self.assertFalse(default_location.special_handling_required)
        self.assertEqual(default_location.utilized_capacity, 0)

# Add additional tests as necessary for other methods and model logic.



