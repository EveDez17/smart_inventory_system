from django.db import models
from django.dispatch import receiver
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.core.validators import RegexValidator

 # STORAGE 

class Zone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey('inventory.Category', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()
    

    def __str__(self):
        return self.name

class Aisle(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='aisles', verbose_name=_("Zone"))
    aisle_letter = models.CharField(
        max_length=5,
        validators=[RegexValidator(r'^[A-Za-z]+$', 'Only letters are allowed for aisle letters.')],
        verbose_name=_("Aisle Letter"),
        help_text=_("Aisle identifier (letters only).")
    )
    history = HistoricalRecords()

    class Meta:
        unique_together = ('zone', 'aisle_letter')
        verbose_name = _("Aisle")
        verbose_name_plural = _("Aisles")

    def __str__(self):
        return f"Aisle {self.aisle_letter} in Zone {self.zone.name}"
    
class Rack(models.Model):
    aisle = models.ForeignKey(Aisle, on_delete=models.CASCADE, related_name='racks', verbose_name=_("Aisle"))
    rack_number = models.CharField(max_length=50, verbose_name=_("Rack Number"))
    history = HistoricalRecords()

    def __str__(self):
        return f"Rack {self.rack_number} in {self.aisle}"

class Level(models.Model):
    rack = models.ForeignKey('Rack', on_delete=models.CASCADE, related_name='levels')
    LEVEL_CHOICES = [
        ('G', 'Ground Floor'),
        ('1', 'Level 1'),
        ('2', 'Level 2'),
        ('3', 'Level 3'),
        ('4', 'Level 4'),
    ]
    level = models.CharField(
        max_length=1,
        choices=LEVEL_CHOICES,
        default='G',
        help_text="Specifies the level within the rack."
    )

    def __str__(self):
        return f"{self.get_level_display()} in Rack {self.rack.rack_number}, Aisle {self.rack.aisle.aisle_letter}"

    
class Location(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Location Code"),
        help_text=_("Unique code for identifying the location.")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        help_text=_("Description of the location.")
    )
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='locations')
    side = models.CharField(
        max_length=1, 
        choices=(
            ('E', 'East'),
            ('W', 'West'),
            ('N', 'North'),
            ('S', 'South'),
        ),
        help_text="Side of the location"
    )
    location_number = models.IntegerField()
    weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00, 
        validators=[MinValueValidator(0.00)]
    )
    TYPE_CHOICES = [
        ('PND', 'PND'), 
        ('Storage', 'Storage'), 
        ('Pick Face', 'Pick Face'), 
        ('Inbound Floor', 'Inbound Floor'), 
        ('Outbound Floor', 'Outbound Floor')
    ]
    type = models.CharField(
        max_length=15, 
        choices=TYPE_CHOICES, 
        default='Storage'
    )
    STATUS_CHOICES = [
        ('empty', 'Empty'), 
        ('full', 'Full'), 
        ('vor', 'Verification Required'), 
        ('urgent_pick', 'Urgent Picking Required'), 
        ('urgent_replenish', 'Urgent Replenishment Required'), 
        ('low_stock', 'Low Stock')
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='empty'
    )
    name = models.CharField(max_length=255, blank=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('level', 'side', 'location_number')
        ordering = ['level', 'side', 'location_number']

    def __str__(self):
        return f"Location {self.location_number} ({self.get_side_display()}) on {self.level}"

    def clean(self):
        """Validate conditions that could affect the location status."""
        if self.weight > 0 and self.status == 'empty':
            raise ValidationError('Location status and weight are inconsistent.')

    def save(self, *args, **kwargs):
        """Save method that includes a pre-save validation."""
        self.full_clean()  # Ensures the model is clean before saving
        super().save(*args, **kwargs)

    def update_status_based_on_sensor_data(self, weight, low_stock_threshold=50, urgent_replenish_threshold=20):
        """Update location status dynamically based on sensor data and type-specific thresholds."""
        self.weight = weight
        if self.type == 'PND':
            self.status = 'empty' if weight == 0 else 'full'
        elif self.type == 'Pick Face':
            if weight == 0:
                self.status = 'empty'
            elif weight <= urgent_replenish_threshold:
                self.status = 'urgent_replenish'
            elif weight <= low_stock_threshold:
                self.status = 'low_stock'
            else:
                self.status = 'full'
        else:
            if weight == 0:
                self.status = 'empty'
            elif weight <= urgent_replenish_threshold:
                self.status = 'urgent_replenish'
            elif weight <= low_stock_threshold:
                self.status = 'low_stock'
            else:
                self.status = 'full'
        self.save()

    @classmethod
    def get_for_full_pallets(cls, product):
        """Retrieve the location for full pallets of a specific product."""
        location = cls.objects.filter(
            stock_levels__product=product, 
            stock_levels__quantity__gte=product.pallet_size
        ).first()
        if not location:
            raise ValueError(f"No full pallets found for product {product.name}.")
        
    def latest_sensor_data(self):
        # This will filter all the sensors related to the location,
        # then get the latest SensorData entry for each of them
        latest_data = []
        for sensor in self.sensors.all():
            latest_data_for_sensor = sensor.data.order_by('-timestamp').first()
            if latest_data_for_sensor:
                latest_data.append({
                    'sensor': sensor,
                    'data': latest_data_for_sensor.data,
                    'timestamp': latest_data_for_sensor.timestamp
                })
        return latest_data

    def __str__(self):
        return f"Location {self.code}"


class PNDLocation(Location):
    temperature_range = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='default-range',  # Providing a default value
        verbose_name=_("Temperature Range"),
        help_text=_("Suitable temperature range for this location, e.g., '0-4°C' for chilled.")
    )
    capacity = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name=_("Capacity"),
        help_text=_("Maximum capacity of the location. Useful for space management.")
    )
    restrictions = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_("Restrictions"),
        help_text=_("Any specific restrictions for this location, such as 'No flammable products'.")
    )
   

    def __str__(self):
        return super().__str__() + " - PND"
    

    
class PickFace(Location):
    pick_face_code = models.CharField(max_length=50, unique=True, verbose_name=_("Pick Face Code"))
    pick_faces = models.ManyToManyField('self', symmetrical=False, blank=True, verbose_name=_("Related Pick Faces"))
    parent_location = models.ForeignKey('self', on_delete=models.CASCADE, related_name='child_pick_faces', null=True, blank=True, verbose_name=_("Parent Location"))
    product = models.ForeignKey('inventory.FoodProduct', on_delete=models.CASCADE, related_name='pick_faces', verbose_name=_("Product"))
    category = models.ForeignKey('inventory.Category', on_delete=models.CASCADE, related_name='pick_faces', verbose_name=_("Category"))
    current_stock = models.PositiveIntegerField(default=0, verbose_name=_("Current Stock"))
    low_stock_threshold = models.PositiveIntegerField(default=10, verbose_name=_("Low Stock Threshold"))
    target_stock_level = models.PositiveIntegerField(default=100, verbose_name=_("Target Stock Level"))
    
    

    def __str__(self):
        return f"{self.pick_face_code} - {super().__str__()} - {self.category.name}"

    def trigger_replenishment(self):
        """Trigger a replenishment task based on stock availability and the required task type."""
        stock_location = self.find_available_stock_location()
        if not stock_location:
            print(f"No stock available for replenishment of {self.pick_face_code}.")
            return

        task_class, task_type = self.determine_task_type(stock_location)
        task_class.objects.create(
            task_type=task_type,
            product=self.product,
            quantity=self.calculate_replenishment_quantity(),
            source_location=stock_location,
            destination_location=self,
            vna_equipment='Default VNA' if task_class == 'outbound.VNATask' else '',
            status='Assigned'
        )
        print(f"Replenishment task created for {self.pick_face_code} from {stock_location}.")

    def find_available_stock_location(self):
        """Find a stock location with sufficient inventory to fulfill a replenishment."""
        return Location.objects.exclude(stock_levels__quantity=0).filter(type__in=['Storage', 'Inbound Floor']).order_by('-stock_levels__quantity').first()

    def determine_task_type(self, stock_location):
        """Determine the appropriate task type based on the location type."""
        if stock_location.type in ['Inbound Floor', 'Outbound Floor']:
            return 'inbound.FLTTask', 'Replenishment'
        else:
            return 'outbound.VNATask', 'Replenishment Picking'

    def calculate_replenishment_quantity(self):
        """Calculate the quantity needed to replenish the pick face to the target level."""
        return max(self.target_stock_level - self.current_stock, 0)

@receiver(post_save, sender=PickFace)
def handle_low_stock_pick_face(sender, instance, **kwargs):
    if instance.current_stock < instance.low_stock_threshold:
        location = instance.find_available_stock_location()
        if location:
            task_class, task_type = instance.determine_task_type(location)
            task_class.objects.create(
                task_type=task_type,
                product=instance.product,
                quantity=instance.calculate_replenishment_quantity(),  # Update method name
                source_location=location,
                destination_location=instance.location,
                status='Assigned'
            )

# IoT Integretion

class Sensor(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='sensors')
    sensor_type = models.CharField(max_length=50, verbose_name=_("Sensor Type"))
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')
    last_checked = models.DateTimeField(auto_now=True, verbose_name=_("Last Checked"))

    def __str__(self):
        return f"{self.sensor_type} Sensor at {self.location.code} - {self.get_status_display()}"

class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='data')
    data = models.JSONField(verbose_name=_("Data"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))

    def __str__(self):
        return f"Data from {self.sensor} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

