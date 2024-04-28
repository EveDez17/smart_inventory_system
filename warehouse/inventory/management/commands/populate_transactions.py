from django.core.management.base import BaseCommand
from django.utils import timezone
from warehouse.inventory.models import Transaction

class Command(BaseCommand):
    help = 'Populates transactions for testing purposes'

    def handle(self, *args, **kwargs):
        # Create some sample transactions
        Transaction.objects.create(
            transaction_type='PAY',
            status='COM',
            amount=100.00,
            description="Payment for goods",
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        Transaction.objects.create(
            transaction_type='REF',
            status='PEN',
            amount=50.00,
            description="Refund for returned items",
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        self.stdout.write(self.style.SUCCESS('Transactions created successfully'))

