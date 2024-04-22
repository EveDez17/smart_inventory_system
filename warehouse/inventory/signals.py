
from django.db.models.signals import post_save
from django.dispatch import receiver
from warehouse.inventory.models import AuditLog, StockLevel
from warehouse.outbound.models import Order


@receiver(post_save, sender=StockLevel)
def handle_low_stock(sender, instance, created, **kwargs):
    if not created and 'quantity' in kwargs.get('update_fields', []):
        if instance.quantity < instance.location.low_stock_threshold:
            instance.location.trigger_replenishment()




@receiver(post_save, sender=Order)
def create_audit_log(sender, instance, created, **kwargs):
    action = 'Created' if created else 'Updated'
    AuditLog.objects.create(
        content_object=instance,
        action=action,
        user=instance.last_updated_by,  # Assuming 'last_updated_by' is a field tracking the last user who updated the entity
        description=f"{action} order with total amount {instance.total_amount}"
    )




