from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import GatehouseBooking, ProvisionalBayAssignment, FinalBayAssignment
from django.utils import timezone

User = get_user_model()

class GatehouseBookingModelTest(TestCase):

    def test_string_representation(self):
        booking = GatehouseBooking(driver_name="John Doe", company="Acme Corp", arrival_time=timezone.now())
        expected_string = f"{booking.driver_name} from {booking.company} with trailer {booking.trailer_number} arrived at {booking.arrival_time.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(booking), expected_string)

    def test_save_method(self):
        booking = GatehouseBooking(
            driver_name="John Doe",
            company="Acme Corp",
            has_paperwork=False
        )
        booking.save()
        # This assertion will pass if the save method correctly sets paperwork_description to "" when has_paperwork is False
        self.assertEqual(booking.paperwork_description, "")

class ProvisionalBayAssignmentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.gatehouse_booking = GatehouseBooking.objects.create(
            driver_name="John Doe",
            company="Acme Corp"
        )

    def test_provisional_bay_assignment(self):
        assignment = ProvisionalBayAssignment(
            gatehouse_booking=self.gatehouse_booking,
            provisional_bay="Bay 1",
            assigned_by=self.user
        )
        assignment.save()
        self.assertEqual(str(assignment), f"Provisional bay Bay 1 assigned to {self.gatehouse_booking}")

class FinalBayAssignmentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('loader', 'loader@example.com', 'loadpass')
        self.gatehouse_booking = GatehouseBooking.objects.create(
            driver_name="John Doe",
            company="Acme Corp"
        )
        self.provisional_bay_assignment = ProvisionalBayAssignment.objects.create(
            gatehouse_booking=self.gatehouse_booking,
            provisional_bay="Bay 1",
            assigned_by=self.user
        )

    def test_final_bay_assignment_and_loading(self):
        final_assignment = FinalBayAssignment(
            provisional_bay_assignment=self.provisional_bay_assignment,
            final_bay="Final Bay 1"
        )
        final_assignment.confirm_loading(self.user)
        final_assignment.save()

        self.assertTrue(final_assignment.is_loaded)
        self.assertIsNotNone(final_assignment.loaded_at)
        self.assertEqual(final_assignment.loader, self.user)
        self.assertEqual(str(final_assignment), f"Final bay Final Bay 1 confirmed for {self.provisional_bay_assignment}, Loaded: Yes, No tipper assigned")

    

