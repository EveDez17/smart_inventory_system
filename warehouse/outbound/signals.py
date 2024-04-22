from django.db.models.signals import post_save
from django.dispatch import receiver
from warehouse.outbound.models import Outbound, VNATask
from warehouse.storage.models import Location, PickFace


@receiver(post_save, sender=PickFace)
def handle_low_stock_pick_face(sender, instance, **kwargs):
    if instance.current_stock < instance.low_stock_threshold:
        location = instance.find_available_stock_location()
        if location:
            task_class, task_type = instance.determine_task_type(location)
            task_class.objects.create(
                task_type=task_type,
                product=instance.product,  # Ensure this relation or attribute exists
                quantity=instance.calculate_needed_quantity(),
                source_location=location,
                destination_location=instance.location,
                status='Assigned'
            )
def trigger_replenishment(self):
    """Trigger a replenishment task based on stock availability and the required task type."""
    stock_location = self.find_available_stock_location()
    if not stock_location:
        print(f"No stock available for replenishment of {self.code}.")
        return

    task_class, task_type = self.determine_task_type(stock_location)
    task_class.objects.create(
        task_type=task_type,
        product=self.category.products.first(),
        quantity=self.calculate_replenishment_quantity(),
        source_location=stock_location,
        destination_location=self.location,
        vna_equipment='Default VNA' if task_class == 'outbound.VNATask' else '',
        status='Assigned'
    )
    print(f"Replenishment task created for {self.code} from {stock_location}.")

def find_available_stock_location(self):
    """Find a stock location with sufficient inventory to fulfill a replenishment."""
    return Location.objects.filter(type__in=['Storage', 'Inbound Floor']).first()

def determine_task_type(self, stock_location):
    """Determine the appropriate task type based on the location type."""
    if stock_location.type in ['Inbound Floor', 'Outbound Floor']:
        return 'inbound.FLTTask', 'Replenishment'
    else:
        return 'outbound.VNATask', 'Replenishment Picking'

def calculate_replenishment_quantity(self):
    """Calculate the quantity needed to replenish the pick face to the target level."""
    return max(self.target_stock_level - self.current_stock, 0)

@receiver(post_save, sender=VNATask)
def create_flt_task_from_vnatask(sender, instance, created, **kwargs):
    if created and instance.status == 'Completed' and instance.task_type == 'Order Picking':
        destination_location = Outbound.get_default_location()
        'inbound.FLTTask'.objects.create(
            task_type='Order Completion',
            product=instance.product,
            quantity=instance.quantity,
            source_location=instance.destination_location,
            destination_location=destination_location,
            status='Pending'
        )