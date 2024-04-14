from celery import shared_task
from inventory.models import Order, OrderItem, Customer, FoodProduct
from django.utils import timezone
import random

@shared_task
def generate_order():
    customer = Customer.objects.order_by('?').first()  # Random customer
    product = FoodProduct.objects.order_by('?').first()  # Random product
    quantity = random.randint(1, 10)  # Random quantity

    order = Order.objects.create(
        customer=customer,
        order_date=timezone.now(),
        total_amount=product.unit_price * quantity,
        status='Pending',
        is_paid=False,
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        unit_price=product.unit_price
    )

    return f"Generated order {order.id} for {customer.name}"
