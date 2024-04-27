from django.conf import settings
from django.db import models
from django.utils import timezone
import joblib
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db import models
from django.db.models import Count, Sum, Max, Avg
from warehouse.storage.models import Location


class HistoricalCategoryModel(models.Model):
    lft = models.IntegerField(null=True, blank=True)
    rght = models.IntegerField(null=True, blank=True)
    tree_id = models.IntegerField(null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True     
          
class Category(MPTTModel):
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_("category name"),
        help_text=_("format: required, max-100"),
    )
    slug = models.SlugField(
        max_length=150,
        null=False,
        blank=False,
        unique=True,  # Ensure URL uniqueness within the system
        verbose_name=_("category safe URL"),
        help_text=_("format: required, letters, numbers, underscore, or hyphens"),
    )
    is_active = models.BooleanField(default=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        null=True,
        blank=True,
        verbose_name=_("parent category"),
        help_text=_("format: not required"),
    )
    pnd_location = models.ForeignKey(
        'storage.PNDLocation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("PND Location"),
        help_text=_("Preferred PND location for this category")
    )
    weight_limit = models.DecimalField(
        max_digits=5,  
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("weight limit"),
        help_text=_("Maximum weight limit for this category in kilograms.")
    )
    history = HistoricalRecords(excluded_fields=['lft', 'rght', 'tree_id', 'level'])

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = _("product category")
        verbose_name_plural = _("product categories")

    def __str__(self):
        return self.name




class Address(models.Model):
    street_number = models.CharField(max_length=128)
    street_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    county = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    post_code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = (('street_number', 'post_code'),)

    def __str__(self):
    
        return f"{self.street_number} {self.street_name}, {self.city}, {self.county}, {self.country}, {self.post_code}"
    
class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("supplier name"))
    contact = models.CharField(max_length=255, verbose_name=_("supplier contact"))
    email = models.EmailField(verbose_name=_("supplier email"))
    contact_number = models.CharField(max_length=50, verbose_name=_("supplier contact number"))
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    address = models.OneToOneField(
        Address,
        on_delete=models.CASCADE,
        related_name='supplier',
        verbose_name=_("address")
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} - {self.email}"
    
class FoodProduct(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    suppliers = models.ManyToManyField(Supplier, related_name='products')
    is_high_demand = models.BooleanField(default=False, help_text=_("Indicates if the product is in high demand"))
    batch_number = models.CharField(max_length=100)
    storage_temperature = models.CharField(max_length=50)
    date_received = models.DateField()
    expiration_date = models.DateField()
    supplier = models.CharField(max_length=255)
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='product_updates')
    updated_at = models.DateTimeField(auto_now=True, null=True)
    stock = models.IntegerField(default=0)
    history = HistoricalRecords()

    def clean(self):
        # Custom validation to disallow negative quantities
        if self.quantity < 0:
            raise ValidationError({"quantity": ["Quantity must be non-negative."]})

    def save(self, *args, **kwargs):
        self.full_clean()  # This calls the clean method and validates the model
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sku}: {self.name} - Batch {self.batch_number}"

    def is_expired(self):
        """Check if the product is expired based on the current date."""
        return self.expiration_date < timezone.now().date()

    class Meta:
        ordering = ['expiration_date']
        
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('Start', _('Task Started')),
        ('Complete', _('Task Completed')),
        ('Interrupt', _('Task Interrupted')),
        ('Update', _('Status Updated')),
        ('Manual', _('Manual Change')),
    ]

    # Generic Foreign Key setup
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        verbose_name=_("Content Type")
    )
    object_id = models.PositiveIntegerField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey('content_type', 'object_id')

    action = models.CharField(
        max_length=50, 
        choices=ACTION_CHOICES, 
        verbose_name=_("Action")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name=_("User")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Timestamp")
    )
    description = models.TextField(
        verbose_name=_("Description"), 
        blank=True, 
        null=True
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")

    def __str__(self):
        return f"{self.content_type.model.capitalize()} ({self.object_id}) - {self.get_action_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

#STOCK LEVEL
    
class StockLevel(models.Model):
    location = models.ForeignKey(
        'storage.Location', 
        on_delete=models.CASCADE, 
        related_name='stock_levels', 
        verbose_name=_("Warehouse Location")
    )
    pick_face = models.ForeignKey(
        'storage.PickFace', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='pick_face_stock_levels',  # Changed related_name to be unique
        verbose_name=_("Pick Face Location")
    )
    product = models.ForeignKey(
        'FoodProduct', 
        on_delete=models.CASCADE, 
        related_name='product_stock_levels',  # Ensuring this related_name is uniquely identifying the relation
        verbose_name=_("Product")
    )
    quantity = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        help_text=_("Current quantity of the product at the location.")
    )
    batch_number = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text=_("Batch number for tracking specific batches of the product")
    )
    expiration_date = models.DateField(
        blank=True, 
        null=True, 
        help_text=_("Expiration date of the product batch")
    )
    last_updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Stock Level")
        verbose_name_plural = _("Stock Levels")
        unique_together = (('location', 'product', 'batch_number'),)
        ordering = ['location', 'product', '-expiration_date']

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units at {self.location}"

    def save(self, *args, **kwargs):
        """Custom save method to handle stock updates."""
        if self.quantity < 0:
            raise ValidationError(_("Quantity cannot be negative."))
        super().save(*args, **kwargs)

    def update_quantity(self, change):
        """Method to update the quantity of stock."""
        if not self.pk:
            raise ValidationError(_("StockLevel instance must be saved before updating quantity."))
        if self.quantity + change < 0:
            raise ValidationError(_("Resulting quantity cannot be negative."))

        with transaction.atomic():
            StockLevel.objects.filter(pk=self.pk).update(quantity=models.F('quantity') + change)
            self.refresh_from_db()

    @classmethod
    def adjust_stock(cls, product_id, location_id, quantity_change):
        """Class method to adjust stock levels."""
        with transaction.atomic():
            stock, created = cls.objects.get_or_create(
                product_id=product_id, 
                location_id=location_id,
                defaults={'quantity': max(quantity_change, 0)}  # Ensure non-negative initial quantity
            )
            if not created:
                stock.update_quantity(quantity_change)

    @classmethod
    def check_for_expired_stock(cls):
        """Class method to find expired stock."""
        today = timezone.now().date()
        return cls.objects.filter(expiration_date__lt=today).order_by('expiration_date')

    @classmethod
    def products_at_location(cls, location_id):
        """Class method to get products at a specific location."""
        return cls.objects.filter(location_id=location_id).select_related('product')

    def is_product_expired(self):
        """Check if the product batch is expired."""
        if not self.expiration_date:
            return False
        today = timezone.now().date()  # Ensures correct handling of time zone
        return today > self.expiration_date
        

class Report(models.Model):
    REPORT_CHOICES = [
        ('inventory', 'Inventory Report'),
        ('order', 'Order Report'),
        ('supplier', 'Supplier Report'),
        ('shipment', 'Shipment Report'),
        ('activity', 'User Activity Report'),
        ('maximums', 'Max Values Report'),  # New type for maximum values report
    ]

    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=100, choices=REPORT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_report(self):
        """ Dispatch to the specific report generator based on the report type. """
        report_generators = {
            'inventory': self.inventory_report,
            'order': self.order_report,
            'supplier': self.supplier_report,
            'shipment': self.shipment_report,
            'activity': self.activity_report,
            'maximums': self.maximums_report,  # Handle maximums report
        }
        report_func = report_generators.get(self.report_type, lambda: "Unsupported report type")
        return report_func()

    def inventory_report(self):
        """ Generate a report summarizing inventory levels across products. """
        data = StockLevel.objects.values('product__name') \
                .annotate(total_stock=Sum('quantity'), max_stock=Max('quantity'), average_price=Avg('product__unit_price')) \
                .order_by('-total_stock')
        return data

    def order_report(self):
        """ Generate a report on orders, categorized by status and aggregated for the past month. """
        data = 'outbound.Order'.objects.filter(order_date__gte=timezone.now() - timezone.timedelta(days=30)) \
                .values('status') \
                .annotate(total_orders=Count('id'), max_order_amount=Max('total_amount'), total_amount=Sum('total_amount')) \
                .order_by('-total_orders')
        return data

    def maximums_report(self):
        """ Generate a report to find the maximum values across various entities. """
        report_data = {
            'max_inventory': StockLevel.objects.aggregate(Max('quantity')),
            'max_order_amount': 'outbound.Order'.objects.aggregate(Max('total_amount')),
            'max_product_price': FoodProduct.objects.aggregate(Max('unit_price')),
            'max_quantity_received': 'inbound.Receiving'.objects.aggregate(Max('quantity')),
            # You can add more fields as required
        }
        return report_data

    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ['-created_at']


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        PAYMENT = 'PAY', _('Payment')
        REFUND = 'REF', _('Refund')
        ADJUSTMENT = 'ADJ', _('Adjustment')

    class TransactionStatus(models.TextChoices):
        PENDING = 'PEN', _('Pending')
        COMPLETED = 'COM', _('Completed')
        FAILED = 'FAI', _('Failed')

    # Basic transaction details
    transaction_type = models.CharField(
        max_length=3,
        choices=TransactionType.choices,
        default=TransactionType.PAYMENT,
        verbose_name=_("Transaction Type")
    )
    status = models.CharField(
        max_length=3,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
        verbose_name=_("Status")
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name=_("Amount")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )

    # References to related entities
    order = models.ForeignKey(
        'outbound.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name=_("Related Order")
    )
    customer = models.ForeignKey(
        'outbound.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name=_("Related Customer")
    )
    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name=_("Related Supplier")
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )

    def __str__(self):
        return f"{self.get_transaction_type_display()} - ${self.amount} - {self.get_status_display()} on {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ['-created_at']


# AI Integresion

class PredictionModel(models.Model):
    name = models.CharField(max_length=255)
    model_file = models.FileField(upload_to='models/')

    def predict(self, X):
        # Load the model from the file each time before making a prediction
        model = joblib.load(self.model_file.path)
        return model.predict(X)

    def __str__(self):
        return self.name


















    





        
        
        
    
