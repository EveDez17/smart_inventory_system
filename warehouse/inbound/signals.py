from warehouse.inbound.models import Inbound, PutawayTask
from django.db.models.signals import post_save
from django.dispatch import receiver
from asyncio.log import logger

@receiver(post_save, sender=Inbound)
def handle_inbound_received(sender, instance, **kwargs):
    if instance.status == 'Received' and (kwargs.get('created', False) or 'status' in kwargs.get('update_fields', [])):
        create_putaway_task_for_inbound(instance)

def create_putaway_task_for_inbound(inbound):
    pnd_location = inbound.product.category.pnd_location if inbound.product.category else None
    if pnd_location:
        PutawayTask.objects.create(
            inbound=inbound,
            pnd_location=pnd_location,
            assigned_to=None,  # Assign based on your business logic
            status='Assigned'
        )
        print(f"Putaway Task created for {inbound.product.name} at PND location {pnd_location}")
    else:
        print(f"No PND location assigned for category {inbound.product.category}, unable to create Putaway Task.")
        
#To ensure all signals pass the tests
@receiver(post_save, sender=Inbound)
def create_putaway_task(sender, instance, created, **kwargs):
    logger.debug(f"Signal triggered for Inbound ID: {instance.pk}, Status: {instance.status}")
    if instance.status == 'Received':
        PutawayTask.objects.create(inbound=instance)
        
@receiver(post_save, sender='storage.Location')
def location_update_handler(sender, instance, created, **kwargs):
    if not created and 'status' in kwargs.get('update_fields', []):
        if instance.status in ['urgent_pick', 'urgent_replenish']:
            'outbound.send_urgent_notification'(instance)
        elif instance.status == 'vor':
            'outbound.send_verification_required_notification'(instance)

#@receiver(post_migrate)
#def create_initial_replenishment_task(sender, **kwargs):
#    product = FoodProduct.objects.first()
#    if product:
#        ReplenishmentTask.objects.create(product=product, quantity=100)
#    else:
 #       print("No products available to create an initial replenishment task.")

