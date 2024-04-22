import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError
from django.utils import timezone
from warehouse.storage.models import Location




User = get_user_model()


class Outbound(Location):  
    address = models.CharField(max_length=255, null=True)
    floor_number = models.PositiveIntegerField()
    bay_number = models.PositiveIntegerField()
    additional_info = models.TextField()
    location_identifier = models.CharField(max_length=100)
    max_capacity = models.IntegerField()
    operational_restrictions = models.CharField(max_length=255)
    special_handling_required = models.BooleanField(default=False)
    history = HistoricalRecords()
    outbound_code = models.CharField(max_length=50, unique=True, verbose_name=_("Outbound Code"))
    related_outbounds = models.ManyToManyField('self', symmetrical=False, blank=True, verbose_name=_("Related Outbounds"))
    managing_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_outbounds', verbose_name=_("Managing User"))
    utilized_capacity = models.PositiveIntegerField(default=0, verbose_name=_("Utilized Capacity"))

    def __str__(self):
        return f"{self.outbound_code} - Floor {self.floor_number} - Bay {self.bay_number}"

    @staticmethod
    def get_default_location():
        unique_criteria = {
            'outbound_code': 'DEFAULT_OUTBOUND',  # Ensuring unique code for default location
            'location_identifier': 'DEFAULT_OUTBOUND'  # Assuming 'location_identifier' needs to be unique as well
        }
        default_location, _ = Outbound.objects.get_or_create(
            defaults={
                'address': 'Default Address',
                'floor_number': 1,
                'bay_number': 1,
                'additional_info': 'Default outbound location',
                'max_capacity': 1000,
                'operational_restrictions': 'None',
                'special_handling_required': False,
                'utilized_capacity': 0
            },
            **unique_criteria
        )
        return default_location




# LLOP TASK MODEL

class LLOPTask(models.Model):
    TASK_CHOICES = [
        ('Picking', _('Picking')),
        ('Replenishing', _('Replenishing')),
    ]

    task_type = models.CharField(
        max_length=20, 
        choices=TASK_CHOICES, 
        default='Picking', 
        help_text=_("Type of LLOP task.")
    )
    product = models.ForeignKey(
        'inventory.FoodProduct', 
        on_delete=models.CASCADE, 
        related_name='llop_tasks', 
        verbose_name=_("Product")
    )
    source_location = models.ForeignKey(
        'storage.PickFace', 
        on_delete=models.CASCADE, 
        related_name='llop_source_tasks', 
        verbose_name=_("Source Location")
    )
    destination_location = models.ForeignKey(
        'Outbound',  # Directly using Outbound which is a specialized Location
        on_delete=models.CASCADE, 
        related_name='llop_destination_tasks', 
        verbose_name=_("Destination Location")
    )
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))
    unit_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text=_("Unit price at the time of task creation")
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_llop_tasks', 
        verbose_name=_("Assigned To")
    )
    status = models.CharField(
        max_length=20, 
        choices=[('Assigned', _('Assigned')), ('In Progress', _('In Progress')), ('Completed', _('Completed'))], 
        default='Assigned', 
        verbose_name=_("Status")
    )
    start_time = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Start Time")
    )
    completion_time = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_("Completion Time")
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.get_task_type_display()} Task for {self.product.name} - {self.quantity} units from {self.source_location} to {self.destination_location}"

    def perform_task(self):
        if self.status != 'Assigned':
            return "Task is already started or completed."
        self.status = 'In Progress'
        self.save()

        if self.source_location.current_stock < self.quantity:
            raise ValueError("Insufficient stock at source.")

        self.source_location.current_stock -= self.quantity
        self.source_location.save()

        destination_stock, _ = 'inventory.StockLevel'.objects.get_or_create(
        location=self.destination_location, product=self.product, defaults={'quantity': 0})
        destination_stock.quantity += self.quantity
        destination_stock.save()

        self.status = 'Completed'
        self.completion_time = timezone.now()
        self.save()
        return "Task completed."

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.product.name} from {self.source_location} to {self.destination_location}"

    def update_stock_levels(self):
        """Adjust stock levels at source and destination based on the task."""
        if self.source_location.current_stock < self.quantity:
            raise ValueError("Insufficient stock at source location to perform the task.")

        self.source_location.current_stock -= self.quantity
        self.source_location.save()

        destination_stock, created = 'inventory.StockLevel'.objects.get_or_create(
            location=self.destination_location,
            product=self.product,
            defaults={'quantity': 0}
        )
        destination_stock.quantity += self.quantity
        destination_stock.save()
        
# VNA TASKS
        
class VNATask(models.Model):
    TASK_TYPES = [
        ('Putaway', 'Putaway from PND to Storage'),
        ('Order Picking', 'Order Picking from Storage to PND'),
        ('Replenishment Picking', 'Replenishment Picking from Storage to PND')
    ]

    task_type = models.CharField(
        max_length=30,
        choices=TASK_TYPES, 
        default='Putaway',
        help_text=_("Type of VNA task.")
    )
    product = models.ForeignKey('inventory.FoodProduct', on_delete=models.CASCADE, related_name='vna_tasks', verbose_name=_("Product"))
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))
    source_location = models.ForeignKey('storage.Location', on_delete=models.CASCADE, related_name='vna_source_tasks', verbose_name=_("Source Location"))
    destination_location = models.ForeignKey('storage.Location', on_delete=models.CASCADE, related_name='vna_destination_tasks', verbose_name=_("Destination Location"))
    vna_equipment = models.CharField(max_length=255, verbose_name=_("VNA Equipment"), help_text=_("The VNA equipment used for this task."))
    status = models.CharField(
        max_length=20, 
        choices=[
            ('Assigned', 'Assigned'), 
            ('In Progress', 'In Progress'), 
            ('Completed', 'Completed')
        ], 
        default='Assigned', 
        verbose_name=_("Status")
    )
    start_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Start Time"))
    completion_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Completion Time"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("VNATask")
        verbose_name_plural = _("VNATasks")

    def __str__(self):
        task_type_display = dict(self.TASK_TYPES).get(self.task_type, "Unknown Task Type")
        return f"{task_type_display} for {self.product.name} from {self.source_location} to {self.destination_location} - {self.status}"

    def save(self, *args, **kwargs):
        creating = not self.pk  # Check if the object is being created
        if self.task_type == 'Putaway' and self.source_location.type != 'PND':
            raise ValidationError("Source location must be a PND type for Putaway tasks.")
        elif self.task_type in ['Order Picking', 'Replenishment Picking'] and self.destination_location.type != 'PND':
            raise ValidationError("Destination location must be a PND type for Picking tasks.")
        
        super().save(*args, **kwargs)  # Call the "real" save method.
        
        if creating and self.status == 'Completed' and self.task_type == 'Order Picking':
            # Assuming FLTTask and Outbound models are defined with a get_default_location method
            'inbound.FLTTask'.objects.create(
                task_type='Order Completion',
                product=self.product,
                quantity=self.quantity,
                source_location=self.destination_location,
                destination_location='outboundOutbound'.get_default_location(),
                status='Pending'
            )
    
logger = logging.getLogger(__name__)
    
class ReplenishmentTask(models.Model):
    source_location = models.ForeignKey('storage.Location', on_delete=models.CASCADE, related_name='replenishment_sources')
    destination_location = models.ForeignKey('storage.Location', null=True, on_delete=models.CASCADE, related_name='replenishment_destinations')
    product = models.ForeignKey('inventory.FoodProduct', on_delete=models.CASCADE, related_name='replenishment_tasks')
    quantity = models.PositiveIntegerField(help_text=_("Quantity to be replenished."))
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='replenishment_tasks')
    priority = models.IntegerField(default=0, help_text=_("Priority of the task, with higher numbers indicating higher priority."))
    history = HistoricalRecords()

    def clean(self):
        """Perform validations before saving the model."""
        if not self.product_id:
            raise ValidationError("Product must be set before saving a ReplenishmentTask.")
        if self.quantity is None:
            raise ValidationError("Quantity must be provided for a ReplenishmentTask.")

    def save(self, *args, **kwargs):
        """Custom save method that includes set_priority call."""
        self.set_priority()  # Adjust priority before saving
        self.clean()  # Validate before saving to ensure data integrity
        super().save(*args, **kwargs)

    def set_priority(self):
        """Set priority based on quantity and product demand."""
        if self.quantity > 100 or (self.product and self.product.is_high_demand):
            self.priority = 100
        else:
            self.priority = 10

    def create_movement_task(self, FLTTask, VNATask, logger, request=None):
        """Create movement task based on the type of source location."""
        try:
            task_class = FLTTask if self.source_location.type == 'Inbound' else VNATask
            task_class.objects.create(
                replenishment_task=self,
                source_location=self.source_location,
                destination_location=self.destination_location,
                product=self.product,
                quantity=self.quantity,
            )
        except Exception as e:
            error_message = f"Error creating movement task: {str(e)}"
            logger.error(error_message)
            if request:
                from django.contrib import messages
                messages.error(request, error_message)
            
class ProductLocation(models.Model):
    product = models.ForeignKey('inventory.FoodProduct', on_delete=models.CASCADE, related_name='locations')
    location = models.ForeignKey('storage.Location', on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField(default=0, help_text=_("Quantity of the product at the location."))
    history = HistoricalRecords()

    class Meta:
        unique_together = ('product', 'location')
        verbose_name = _("Product Location")
        verbose_name_plural = _("Product Locations")

    def __str__(self):
        return f"{self.product.name} at {self.location}"
    
class PickingTaskBase(models.Model):
    """
    Abstract base class for picking tasks, providing common attributes.
    """
    product = models.ForeignKey('inventory.FoodProduct', on_delete=models.CASCADE, related_name='%(class)s_products')
    source_location = models.ForeignKey('storage.Location', on_delete=models.CASCADE, related_name='%(class)s_source')
    destination_location = models.ForeignKey('storage.PNDLocation', on_delete=models.CASCADE, related_name='%(class)s_destination')
    quantity = models.PositiveIntegerField()
    vna_equipment = models.CharField(max_length=255, verbose_name=_("VNA Equipment"), help_text=_("VNA equipment used for the task."))
    status = models.CharField(max_length=20, choices=[('Pending', _('Pending')), ('In Progress', _('In Progress')), ('Completed', _('Completed'))], default='Pending')
    start_time = models.DateTimeField(default=timezone.now)
    completion_time = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.product.name} from {self.source_location} to {self.destination_location} [{self.status}]"



class ReplenishmentPickingTask(PickingTaskBase):
    """
    Task for replenishing stock from storage to PND locations.
    """
    replenishment_request = models.ForeignKey('ReplenishmentRequest', on_delete=models.CASCADE, related_name='picking_tasks', verbose_name=_("Replenishment Request"))
    
    
    class Meta:
        verbose_name = _("Replenishment Picking Task")
        verbose_name_plural = _("Replenishment Picking Tasks")
        
class ReplenishmentRequest(models.Model):
    product = models.ForeignKey('inventory.FoodProduct', on_delete=models.CASCADE)
    required_quantity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,  # Adjusted for realistic option length
        choices=[
            ('Requested', 'Requested'),
            ('Fulfilling', 'Fulfilling'),
            ('Completed', 'Completed')
        ],
        default='Requested'  # Set default status directly in the field definition
    )
    created_at = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()

    def __str__(self):
        return f"Replenishment request for {self.product.name}, Quantity: {self.required_quantity}"
    
class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Customer Name"))
    email = models.EmailField(verbose_name=_("Customer Email"), unique=True)
    phone = models.CharField(max_length=20, verbose_name=_("Contact Phone"), blank=True)
    address = models.OneToOneField(
        'inventory.Address', 
        on_delete=models.CASCADE, 
        related_name='customer',  # Changed to singular since it's one-to-one
        verbose_name=_("Address")
    )
    history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.name} - {self.email}"

class Order(models.Model):
    customer = models.ForeignKey(
        'Customer', 
        on_delete=models.CASCADE, 
        related_name='orders', 
        verbose_name=_("Customer")
    )
    order_date = models.DateTimeField(default=timezone.now, verbose_name=_("Order Date"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', _('Pending')),
            ('Processing', _('Processing')),
            ('Shipped', _('Shipped')),
            ('Cancelled', _('Cancelled'))
        ],
        default='Pending',
        verbose_name=_("Status")
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Total Amount"))
    is_paid = models.BooleanField(default=False, verbose_name=_("Is Paid"))
    payment_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Payment Date"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Additional Notes"))
    history = HistoricalRecords()

    class Meta:
        ordering = ['-order_date']
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"

    def complete_order(self):
        if self.status not in ['Pending', 'Processing']:
            return f"Order {self.id} cannot be completed from its current state ({self.status})."

        try:
            tasks = []
            for item in self.items.all():
                source = 'storage.Location'.get_for_full_pallets(item.product)
                destination = Outbound.get_default_location()
                task = self.create_flt_task('Order Completion', item.product, item.quantity, source, destination, None)
                tasks.append(task)
            self.status = 'Shipped'
            self.save()

            # Dispatch creation assumes that transport details are provided somehow
            dispatch = Dispatch.objects.create(
                order=self,
                dispatched_by=None,  # Typically set by context or user session
                driver_name="John Doe",
                vehicle_registration="XYZ 1234",
                trailer_number="TR 5678"
            )

            # Create loader tasks for each FLT task
            for task in tasks:
                LoaderTask.objects.create(
                    dispatch=dispatch,
                    product=task.product,
                    quantity=task.quantity,
                    source_location=task.destination_location,
                    status='Pending'
                )

            return f"Order {self.id} completed and marked as shipped. Dispatch ID: {dispatch.id}"
        except ValueError as e:
            return str(e)

    def create_flt_task(self, task_type, product, quantity, source, destination, assigned_to):
        if quantity <= 0:
            raise ValueError("Quantity must be positive and sufficient for transfer.")
        return 'inbound.FLTTask'.objects.create(
            task_type=task_type,
            product=product,
            quantity=quantity,
            source_location=source,
            destination_location=destination,
            assigned_to=assigned_to,
            status='Pending'
        )

    def generate_invoice(self):
        items = self.items.all()
        invoice_lines = [f"Invoice for Order {self.id} - {self.customer.name}\n"]
        invoice_lines.append(f"Order Date: {self.order_date.strftime('%Y-%m-%d %H:%M')}\n")
        invoice_lines.append(f"Status: {self.get_status_display()}\n")
        invoice_lines.append("Items:\n")
        
        for item in items:
            invoice_lines.append(f" - {item.product.name}, Quantity: {item.quantity}, Unit Price: ${item.unit_price}, Total: ${item.total_price}\n")
        
        invoice_lines.append(f"Total Amount: ${self.total_amount}\n")
        invoice_lines.append(f"Paid: {'Yes' if self.is_paid else 'No'}\n")
        
        if self.is_paid:
            invoice_lines.append(f"Payment Date: {self.payment_date.strftime('%Y-%m-%d %H:%M')}\n")
        
        return "".join(invoice_lines)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_("Order"))
    product = models.ForeignKey('inventory.FoodProduct', on_delete=models.SET_NULL, null=True, related_name='order_items', verbose_name=_("Product"))
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Unit Price"))
    history = HistoricalRecords()
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
class OrderPickingTask(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    source_location = models.ForeignKey(
        'storage.Location', 
        on_delete=models.CASCADE,
        related_name='tasks_as_source',
        verbose_name="Source Location"
    )
    destination_location = models.ForeignKey(
        'Outbound', 
        on_delete=models.CASCADE,
        related_name='tasks_as_destination',
        verbose_name="Destination Location"
    )
    product = models.ForeignKey('inventory.FoodProduct', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    vna_equipment = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    completion_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10)
    history = HistoricalRecords()

    def __str__(self):
        return f"Task for Order {self.order.id} - {self.quantity} units from {self.source_location} to {self.destination_location}"
    
class Dispatch(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='dispatch')
    dispatch_time = models.DateTimeField(default=timezone.now, verbose_name=_("Dispatch Time"))
    dispatched_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Dispatched By"))
    driver_name = models.CharField(max_length=255, verbose_name=_("Driver Name"))
    vehicle_registration = models.CharField(max_length=255, verbose_name=_("Vehicle Registration"))
    trailer_number = models.CharField(max_length=255, verbose_name=_("Trailer Number"))
    final_bay_assignment = models.ForeignKey('inbound.FinalBayAssignment', on_delete=models.SET_NULL, null=True, verbose_name=_("Final Bay Assignment"))
    history = HistoricalRecords()

    def finalize_dispatch(self):
        if not self.final_bay_assignment.is_loaded:
            return "Cannot dispatch. Vehicle loading not confirmed."
        self.dispatch_time = timezone.now()
        self.save()
        return f"Dispatch finalized for {self.driver_name}. Departure at {self.dispatch_time.strftime('%Y-%m-%d %H:%M')}."

    def __str__(self):
        return f"Dispatch for Order {self.order.id} - Vehicle {self.vehicle_registration} - Trailer {self.trailer_number} at {self.dispatch_time.strftime('%Y-%m-%d %H:%M')}"

class LoaderTask(models.Model):
    dispatch = models.ForeignKey('Dispatch', on_delete=models.CASCADE, related_name='loader_tasks')
    product = models.ForeignKey('inventory.FoodProduct', on_delete=models.CASCADE, verbose_name=_("Product"))
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))
    source_location = models.ForeignKey('storage.Location', on_delete=models.CASCADE, verbose_name=_("Source Location"))
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')],
        default='Pending',
        verbose_name=_("Status")
    )
    completion_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Completion Time"))
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Confirmed By"))
    history = HistoricalRecords()

    def __str__(self):
        return f"Loader Task for {self.product.name}, Quantity: {self.quantity} - Status: {self.get_status_display()}"

class CMR(models.Model):
    dispatch = models.OneToOneField('Dispatch', on_delete=models.CASCADE, related_name='cmr')
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Confirmed By"))
    document = models.FileField(upload_to='cmr_documents/', verbose_name=_("CMR Document"))
    history = HistoricalRecords()

    def __str__(self):
        return f"CMR Document for Dispatch {self.dispatch.id} created at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Shipment(models.Model):
    dispatch = models.OneToOneField(Dispatch, on_delete=models.CASCADE, related_name='shipment')
    shipment_time = models.DateTimeField(default=timezone.now, verbose_name=_("Shipment Time"))
    shipped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("Shipped By"))
    tracking_number = models.CharField(max_length=255, verbose_name=_("Tracking Number"), null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Shipment for Dispatch {self.dispatch.order.id} - Shipped at {self.shipment_time.strftime('%Y-%m-%d %H:%M')}"     
