from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from warehouse.inventory.models import OrderPickingTask


def get_orders_to_fulfill():
    # Implement your logic to get orders that need to be fulfilled
    pass

# Assuming you have a view or management command to trigger order picking
def trigger_order_picking(request):
    orders = get_orders_to_fulfill()
    for order in orders:
        # Create OrderPickingTask for each order
        OrderPickingTask.objects.create(
            order=order,
            # You need to specify the appropriate values for source_location and destination_location
            source_location=None,  # Specify the source PND location
            destination_location=None,  # Specify the destination Outbound location
            quantity=order.get_total_quantity(),  # Get the total quantity of the order
            vna_equipment='Your VNA Equipment',  # Specify the VNA equipment
            status='Pending',  # Set the initial status of the task
        )


def notify_vna_operator_of_new_task(operator, task):
    """
    Notify a VNA operator of a new task using WebSockets.
    
    :param operator: The operator user instance.
    :param task: The VNATask instance.
    """
    channel_layer = get_channel_layer()
    group_name = f'vna_notifications_{operator.id}'  # Assuming operators subscribe to their notification channels

    # Prepare the message
    message = {
        'type': 'vna.task.notification',  # Custom event type
        'message': {
            'task_id': task.id,
            'task_description': f"New task for {task.inbound.product.name} to {task.final_location}",
            'vna_equipment': task.vna_equipment,
            'status': task.status,
        }
    }

    # Send message to group
    async_to_sync(channel_layer.group_send)(
        group_name,
        message
    )
    
def create_flt_task(task_type, product, quantity, source, destination, assigned_to):
    from .models import FLTTask  # Local import inside the function
    if quantity <= 0:
        raise ValueError("Quantity must be positive and sufficient for transfer.")
    return FLTTask.objects.create(
        task_type=task_type,
        product=product,
        quantity=quantity,
        source_location=source,
        destination_location=destination,
        assigned_to=assigned_to,
    )