import random
from datetime import timedelta
from django.utils import timezone

from warehouse.inventory.models import FoodProduct, StockLevel
from warehouse.storage.models import Location, PickFace


# Example: create 10 stock level instances
for _ in range(10):
    # Replace these with actual instances from your database
    location = Location.objects.order_by('?').first()
    pick_face = PickFace.objects.order_by('?').first()
    product = FoodProduct.objects.order_by('?').first()

    quantity = random.randint(0, 100)  # Random quantity between 0 and 100
    batch_number = f"BN{random.randint(1000, 9999)}"  # Random batch number
    expiration_date = timezone.now().date() + timedelta(days=random.randint(0, 100))  # Random expiration date within the next 100 days

    stock_level = StockLevel(
        location=location,
        pick_face=pick_face,
        product=product,
        quantity=quantity,
        batch_number=batch_number,
        expiration_date=expiration_date
    )
    stock_level.save()

print("Stock levels created!")
