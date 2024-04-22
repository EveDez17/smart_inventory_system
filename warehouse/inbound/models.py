from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from warehouse.inventory.models import FoodProduct, PNDLocation, PickFace, Supplier
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()

# Gatehouse Register

class GatehouseBooking(models.Model):
    driver_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    vehicle_registration = models.CharField(max_length=50)
    trailer_number = models.CharField(max_length=50, verbose_name=_("Trailer Number"))
    arrival_time = models.DateTimeField(default=timezone.now)
    has_paperwork = models.BooleanField(default=False)
    paperwork_description = models.CharField(max_length=255, blank=True)
    cancelled = models.BooleanField(default=False)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # If has_paperwork is False, clear the paperwork_description field
        if not self.has_paperwork:
            self.paperwork_description = ""
        super(GatehouseBooking, self).save(*args, **kwargs)
    

    def __str__(self):
        return f"{self.driver_name} from {self.company} with trailer {self.trailer_number} arrived at {self.arrival_time.strftime('%Y-%m-%d %H:%M')}"

class ProvisionalBayAssignment(models.Model):
    gatehouse_booking = models.OneToOneField(GatehouseBooking, on_delete=models.CASCADE)
    provisional_bay = models.CharField(max_length=50)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()

    def __str__(self):
        return f"Provisional bay {self.provisional_bay} assigned to {self.gatehouse_booking}"

class FinalBayAssignment(models.Model):
    provisional_bay_assignment = models.OneToOneField(ProvisionalBayAssignment, on_delete=models.CASCADE)
    final_bay = models.CharField(max_length=50)
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    confirmed_at = models.DateTimeField(default=timezone.now)
    is_loaded = models.BooleanField(default=False, verbose_name=_("Loading Confirmed"))
    loaded_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Loaded At"))
    loader = models.ForeignKey(User, related_name='loaded_bays', on_delete=models.SET_NULL, null=True, verbose_name=_("Loader"))
    history = HistoricalRecords()

    def confirm_loading(self, loader_user):
        if not self.is_loaded:
            self.is_loaded = True
            self.loaded_at = timezone.now()
            self.loader = loader_user
            self.save()
            return "Loading confirmed, vehicle ready for departure."
        return "Loading already confirmed."

    def __str__(self):
        return f"Final bay {self.final_bay} confirmed for {self.provisional_bay_assignment}, Loaded: {self.is_loaded}"


# Inbound class

class Inbound(models.Model):
    final_bay_assignment = models.OneToOneField(FinalBayAssignment, on_delete=models.CASCADE, related_name='inbounds')
    product = models.ForeignKey(FoodProduct, on_delete=models.CASCADE, related_name='inbounds')
    quantity = models.PositiveIntegerField(verbose_name=_("quantity received"))
    receiving_date = models.DateTimeField(default=timezone.now, verbose_name=_("receiving date"))
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("received by"), related_name='inbound_receivings')
    notes = models.TextField(blank=True, null=True, verbose_name=_("additional notes"))
    STATUS_CHOICES = [
        ('Pending', _('Pending Release')),  # Load is awaiting admin release
        ('Received', _('Received')),  # Admin has released the load, and it's acknowledged
        ('Released', _('Released for Putaway')),  # The load is acknowledged and ready for putaway
        ('Stored', _('Stored')),  # The putaway process is complete, and the load is stored
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name=_("Status"))
    floor_location = models.CharField(max_length=100, verbose_name=_("Floor Location"), help_text=_("Location on the warehouse floor where the stock is placed"))
    history = HistoricalRecords()

    def __str__(self):
        return f"Received {self.product.name} in bay {self.final_bay_assignment.final_bay} on {self.receiving_date.strftime('%Y-%m-%d %H:%M')}, Status: {self.get_status_display()}"

    def update_status(self, new_status):
        """Update the status of the inbound record with checks."""
        if new_status not in [choice[0] for choice in self.STATUS_CHOICES]:
            raise ValueError("Invalid status")
        if new_status == 'Released' and self.status != 'Pending':
            raise ValueError("Can only release loads that are pending.")
        self.status = new_status
        self.save()

        # Placeholder for additional actions based on the new status
        if new_status == 'Released':
            # Placeholder for actions to take when load is released for putaway
            # Implement actions here (e.g., create PutawayTask or send notification)
            pass

    class Meta:
        verbose_name = _("Inbound Record")
        verbose_name_plural = _("Inbound Records")
        ordering = ['-receiving_date']
    
class Receiving(models.Model):
    product = models.ForeignKey(
        FoodProduct,
        on_delete=models.CASCADE,
        related_name='receivings',  # This establishes the one-to-many relationship
        verbose_name=_("received product"),
        help_text=_("Select product being received")
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("quantity received"),
        help_text=_("Enter quantity of product received")
    )
    receiving_date = models.DateField(
        default=timezone.now,
        verbose_name=_("receiving date"),
        help_text=_("Date when product was received")
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='receivings',  # Each supplier can have multiple receivings, but this line primarily impacts the product-receiving relationship
        verbose_name=_("supplier"),
        help_text=_("Select supplier of the received product")
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_by',  # Similar to 'product', establishes a one-to-many relationship: one user can receive many products
        verbose_name=_("received by"),
        help_text=_("User who received the product")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("additional notes"),
        help_text=_("Any additional notes about the receiving")
    )
    history = HistoricalRecords()  # Tracks changes to each receiving record, implicitly a one-to-many relationship (each receiving record can have multiple history entries)

    class Meta:
        verbose_name = _("Receiving")
        verbose_name_plural = _("Receivings")
        ordering = ['-receiving_date']

    def __str__(self):
        return f"{self.product.name} received from {self.supplier.name} on {self.receiving_date}"
    
class PutawayTask(models.Model):
    inbound = models.ForeignKey(Inbound, on_delete=models.CASCADE, related_name='putaway_tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='putaway_tasks', verbose_name=_("Assigned FLT Driver"))
    pnd_location = models.ForeignKey(PNDLocation, on_delete=models.SET_NULL, null=True, verbose_name=_("PND Location"), help_text=_("Final destination in the PND location"))
    pick_face = models.ForeignKey(PickFace, on_delete=models.SET_NULL, null=True, verbose_name=_("Pick Face"), help_text=_("Designated pick face for replenishment"))
    status = models.CharField(max_length=20, choices=[('Assigned', _('Assigned')), ('In Progress', _('In Progress')), ('Completed', _('Completed'))], default='Assigned', verbose_name=_("Status"))
    start_time = models.DateTimeField(auto_now_add=True, verbose_name=_("Start Time"))
    completion_time = models.DateTimeField(null=True, blank=True, verbose_name=_("Completion Time"))
    history = HistoricalRecords()

    def __str__(self):
        return f"Putaway Task for {self.inbound.product.name}, PND: {self.pnd_location}, assigned to {self.assigned_to}, status: {self.status}"

