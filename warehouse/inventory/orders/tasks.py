from celery import shared_task
from inventory.models import Order, OrderItem, Customer, FoodProduct, PredictionModel
from django.utils import timezone
import random
import numpy as np

@shared_task
def generate_order():
    customer = Customer.objects.order_by('?').first()  # Random customer
    product = FoodProduct.objects.order_by('?').first()  # Random product
    quantity = random.randint(1, 10)  # Random quantity

    # Example: Predict the quantity instead of random
    model = PredictionModel.objects.first()  # Assuming you load your model here
    predicted_quantity = model.predict(np.array([[product.id, timezone.now().month]]))  # Example feature array

    order = Order.objects.create(
        customer=customer,
        order_date=timezone.now(),
        total_amount=product.unit_price * predicted_quantity,
        status='Pending',
        is_paid=False,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=predicted_quantity,
        unit_price=product.unit_price
    )

    return f"Generated order {order.id} for {customer.name} with predicted quantity {predicted_quantity}"
