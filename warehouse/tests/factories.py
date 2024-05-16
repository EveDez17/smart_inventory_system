from datetime import datetime, timedelta
import factory
from faker import Faker
import random
from django.core.exceptions import ValidationError
from django.utils import timezone
from factory.django import DjangoModelFactory
from factory import Faker, Sequence, LazyAttribute, Iterator, RelatedFactoryList
from pytest_factoryboy import register
from warehouse.inbound.models import FLTTask, FinalBayAssignment, GatehouseBooking, Inbound, ProvisionalBayAssignment, PutawayTask, Receiving
from warehouse.inventory import models
from warehouse.outbound.models import Customer, LLOPTask, Order, OrderItem, OrderPickingTask, Outbound, ProductLocation, ReplenishmentPickingTask, ReplenishmentRequest, ReplenishmentTask, VNATask
from warehouse.storage.models import Aisle, Level, Location, PNDLocation, PickFace, Rack, Zone
import factory

fake = Faker('en_US')



class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = models.Category

    name = factory.Sequence(lambda n: f"Category{n}")
    slug = factory.LazyAttribute(lambda x: f"category-{random.randint(1000, 9999)}")

register(CategoryFactory)

class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Address

    street_number = factory.Sequence(lambda n: f"{1000 + n}")
    street_name = factory.Faker('street_name')
    city = factory.Faker('city')
    county = factory.Faker('state')
    country = factory.Faker('country')
    post_code = factory.Faker('postcode')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)



class SupplierFactory(DjangoModelFactory):
    class Meta:
        model = models.Supplier

    name = factory.Faker('company')
    contact = factory.Faker('name')
    email = factory.Faker('email')
    contact_number = factory.Faker('phone_number')
    address = factory.SubFactory(AddressFactory)

register(SupplierFactory)




class FoodProductFactory(DjangoModelFactory):
    class Meta:
        model = models.FoodProduct

    sku_sequence = Sequence(lambda n: f"SKU{n:05d}")  # Define a sequence for SKUs

    sku = LazyAttribute(lambda o: next(o.sku_sequence))  # Use sku_sequence attribute to generate unique SKUs
    name = Faker('name')
    description = Faker('sentence')
    quantity = Faker('random_int', min=1, max=1000)  # Ensures quantity is always non-negative
    unit_price = Faker('pydecimal', right_digits=2, positive=True, min_value=1, max_value=100)
    category = factory.SubFactory(CategoryFactory)
    suppliers = RelatedFactoryList(
        SupplierFactory,
        factory_related_name='products',
        size=3  # Assumes each product has 3 suppliers
    )
    is_high_demand = Faker('boolean')
    batch_number = Sequence(lambda n: f"Batch{n:03d}")
    storage_temperature = Iterator(["0°C-4°C", "5°C-10°C", "Ambient"])
    date_received = Faker('date_this_decade')
    expiration_date = LazyAttribute(lambda o: o.date_received + timedelta(days=365))
    supplier = Faker('company')
    last_updated_by = None  # No user associated
    updated_at = factory.LazyFunction(timezone.now)
    stock = Faker('random_int', min=0, max=1000)

    @factory.post_generation
    def add_suppliers(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for supplier in extracted:
                self.suppliers.add(supplier)


class ReceivingFactory(DjangoModelFactory):
    class Meta:
        model = Receiving
        skip_postgeneration_save = True

    product = factory.SubFactory(FoodProductFactory)
    quantity = factory.Faker('random_number', digits=3)
    receiving_date = factory.LazyFunction(timezone.now)
    supplier = factory.SubFactory(SupplierFactory)
    received_by = None  # Skip creating a User instance
    notes = factory.Faker('text', max_nb_chars=200)
    
    # If you need the User sometimes, you can use a post_generation hook
    @factory.post_generation
    def set_received_by(self, create, extracted, **kwargs):
        if extracted:
            self.received_by = extracted
        self.save()
        
# GATEHOUSE SECURITY TEST MODEL

class GatehouseBookingFactory(DjangoModelFactory):
    class Meta:
        model = GatehouseBooking

    driver_name = factory.Faker('name')
    company = factory.Faker('company')
    vehicle_registration = factory.Faker('bothify', text='???-####', letters='ABCDEFGHKLMNPRSTUVWXYZ')
    trailer_number = factory.Faker('bothify', text='####', letters='ABCDEFGHKLMNPRSTUVWXYZ')
    arrival_time = factory.LazyFunction(timezone.now)
    paperwork = factory.django.FileField(filename='paperwork.pdf')

register(GatehouseBookingFactory)

class ProvisionalBayAssignmentFactory(DjangoModelFactory):
    class Meta:
        model = ProvisionalBayAssignment
        skip_postgeneration_save=True 

    gatehouse_booking = factory.SubFactory(GatehouseBookingFactory)
    provisional_bay = factory.Sequence(lambda n: f"Provisional Bay {n}")
    assigned_by = None  # Skip creating a User instance

    @factory.post_generation
    def set_assigned_by(self, create, extracted, **kwargs):
        if extracted:
            self.assigned_by = extracted
        self.save()

register(ProvisionalBayAssignmentFactory)

class FinalBayAssignmentFactory(DjangoModelFactory):
    class Meta:
        model = FinalBayAssignment
        skip_postgeneration_save=True

    provisional_bay_assignment = factory.SubFactory(ProvisionalBayAssignmentFactory)
    final_bay = factory.Sequence(lambda n: f"Final Bay {n}")
    confirmed_by = None

    @factory.post_generation
    def set_confirmed_by(self, create, extracted, **kwargs):
        if extracted:
            self.confirmed_by = extracted
        self.save()


register(FinalBayAssignmentFactory)

class InboundFactory(DjangoModelFactory):
    class Meta:
        model = Inbound
        skip_postgeneration_save = True

    final_bay_assignment = factory.SubFactory(FinalBayAssignmentFactory)
    product = factory.SubFactory(FoodProductFactory)
    quantity = factory.LazyFunction(lambda: fake.random_int(min=1, max=100))
    receiving_date = factory.LazyFunction(timezone.now)
    received_by = None  # Assuming a User model factory is available, replace None with UserFactory or similar
    notes = factory.Faker('text', max_nb_chars=200)
    status = "Pending"
    floor_location = factory.Sequence(lambda n: f"Floor{n}")

    @factory.post_generation
    def set_received_by(self, create, extracted, **kwargs):
        if extracted:
            self.received_by = extracted
        self.save()

register(InboundFactory)



# STORAGE TEST MODEL
    
class ZoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Zone

    name = factory.Faker('word')
    description = factory.Faker('paragraph')
    category = factory.SubFactory(CategoryFactory)

class AisleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Aisle

    zone = factory.SubFactory(ZoneFactory)
    aisle_letter = factory.Sequence(lambda n: chr(65 + n % 26))  # Cycles through A-Z

class RackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rack

    aisle = factory.SubFactory(AisleFactory)
    rack_number = factory.Sequence(lambda n: f"R{1000 + n}")

class LevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Level

    rack = factory.SubFactory(RackFactory)
    level = factory.Iterator([choice[0] for choice in Level.LEVEL_CHOICES])

class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location
        django_get_or_create = ('code',)

    code = factory.Sequence(lambda n: f"LOC_{n:04d}")
    name = factory.Faker('word')
    level = factory.SubFactory(LevelFactory)
    side = factory.Iterator(['E', 'W'])
    location_number = factory.Sequence(lambda n: n + 1)
    type = factory.Iterator(['PND', 'Storage'])
    status = factory.Iterator([status[0] for status in Location.STATUS_CHOICES])
    description = factory.Faker('sentence')  
    weight = factory.LazyAttribute(lambda o: 0.00 if o.status == 'empty' else 100.00)

    @factory.post_generation
    def validate_model(obj, create, extracted, **kwargs):
        try:
            obj.full_clean()  # Validate model instance to ensure all fields meet the model's constraints
        except ValidationError as e:
            raise ValidationError(f"Error in LocationFactory with code {obj.code}: {e.messages}")

class PNDLocationFactory(LocationFactory):
    class Meta:
        model = PNDLocation
        skip_postgeneration_save = True

    temperature_range = factory.Iterator(["2-4°C", "5-10°C", "None"])
    capacity = factory.Faker('random_number', digits=3)
    restrictions = factory.Faker('sentence', nb_words=8)

    @factory.post_generation
    def set_temperature_range(self, create, extracted, **kwargs):
        # This method allows customization of temperature_range after the factory has done its basic setup
        if extracted:
            self.temperature_range = extracted
    
     
  

#INBOUND TASK TEST MODEL

class PutawayTaskFactory(DjangoModelFactory):
    class Meta:
        model = PutawayTask
        skip_postgeneration_save = True

    inbound = factory.SubFactory(InboundFactory)
    assigned_to = None  # Assuming a User model factory is available, replace None with UserFactory or similar
    pnd_location = factory.SubFactory(PNDLocationFactory)
    status = "Assigned"
    start_time = factory.LazyFunction(timezone.now)
    completion_time = None  # Optionally set to a specific time or leave as None

    @factory.post_generation
    def set_assigned_to(self, create, extracted, **kwargs):
        if extracted:
            self.assigned_to = extracted
        self.save()

register(PutawayTaskFactory)

#VNA TASK TEST MODEL


class VNATaskFactory(DjangoModelFactory):
    class Meta:
        model = VNATask
        skip_postgeneration_save = True 

    task_type = factory.Iterator(['Putaway', 'Order Picking', 'Replenishment Picking'])
    product = factory.SubFactory(FoodProductFactory)
    quantity = factory.Faker('random_int', min=1, max=100)
    source_location = factory.SubFactory(LocationFactory)
    destination_location = factory.SubFactory(LocationFactory)
    vna_equipment = factory.Faker('word')
    status = factory.Iterator(['Assigned', 'In Progress', 'Completed'])

    # Use LazyAttribute for conditional logic instead of Maybe for clarity and control
    @factory.lazy_attribute
    def completion_time(self):
        if self.status == 'Completed':
            return timezone.now()  # Ensure timezone support
        return None

    notes = factory.Faker('text', max_nb_chars=200)

    @factory.post_generation
    def is_completed(self, create, extracted, **kwargs):
        # This method seems redundant if the correct time is being set above
        # If it's necessary to adjust or fix times post-creation, you can keep this logic
        if not create:
            return
        if self.status == 'Completed' and not self.completion_time:
            self.completion_time = datetime.now()  # Consider using timezone.now() here as well
        self.save()

    @classmethod
    def _after_postgeneration(cls, obj, create, results, **kwargs):
        # This method is typically used for more complex post-generation logic
        # If not needed, it can be omitted or left as a pass-through
        super()._after_postgeneration(obj, create, results, **kwargs)
    
class BaseVNATaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VNATask
        abstract = True  # This makes BaseVNATaskFactory not to be used directly

    product = factory.SubFactory(FoodProductFactory)
    quantity = factory.Sequence(lambda n: n + 10)  # Start from 10 to avoid zero
    vna_equipment = "VNA123"
    status = "Assigned"
    start_time = factory.LazyFunction(timezone.now)
    completion_time = None
    notes = factory.Faker('text')

class PutawayVNATaskFactory(BaseVNATaskFactory):
    task_type = 'Putaway'
    product = factory.SubFactory(FoodProductFactory)
    source_location = factory.SubFactory(LocationFactory, type='PND', side='E', location_number=100)
    destination_location = factory.SubFactory(LocationFactory, type='Storage', side='W', location_number=101)

class OrderPickingVNATaskFactory(BaseVNATaskFactory):
    task_type = 'Order Picking'
    source_location = factory.SubFactory(LocationFactory, level_type='Storage')
    destination_location = factory.SubFactory(LocationFactory, level_type='PND')

class ReplenishmentPickingVNATaskFactory(BaseVNATaskFactory):
    task_type = 'Replenishment Picking'
    source_location = factory.SubFactory(LocationFactory, level_type='Storage')
    destination_location = factory.SubFactory(LocationFactory, level_type='PND')
    
    
    
    
class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer
        

    # Ensure the 'id' field is generated automatically
    id = factory.Sequence(lambda n: n)
    name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    address = factory.SubFactory(AddressFactory)
    


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    # Define attributes for the Order object, including customer_id
    customer = factory.SubFactory(CustomerFactory)  # Assuming CustomerFactory creates valid customers

    # Other fields of the Order model
    order_date = factory.LazyFunction(timezone.now)
    status = 'Pending'
    total_amount = 0.00
    is_paid = False
    payment_date = None
    notes = factory.Faker('text')
    
class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(FoodProductFactory)  # Assuming FoodProductFactory is already defined
    quantity = factory.Faker('random_int', min=1, max=10)
    unit_price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    
        
class ReplenishmentTaskFactory(DjangoModelFactory):
    class Meta:
        model = ReplenishmentTask
        skip_postgeneration_save=True
        django_get_or_create = ('product', 'source_location', 'destination_location')

    source_location = factory.SubFactory(LocationFactory)
    destination_location = factory.SubFactory(LocationFactory)
    product = factory.SubFactory(FoodProductFactory)
    quantity = factory.Faker('random_int', min=1, max=500)
    status = factory.Iterator(['Pending', 'In Progress', 'Completed'])
    assigned_to = None  # Explicit handling of None
    priority = factory.LazyAttribute(lambda obj: 100 if obj.quantity > 100 or obj.product.is_high_demand else 10)

    @factory.post_generation
    def set_priority_and_save(self, create, extracted, **kwargs):
        if not create:
            return
        self.save()  # Save to reflect changes in priority

     
class FLTTaskFactory(DjangoModelFactory):
    class Meta:
        model = FLTTask
        skip_postgeneration_save = True  # Optional, depending on whether you want to control save behavior explicitly
        
    task_type = factory.Iterator(['Putaway', 'Order Completion', 'Replenishment'])
    product = factory.SubFactory(FoodProductFactory)
    source_location = factory.SubFactory(LocationFactory)
    destination_location = factory.SubFactory(LocationFactory)
    quantity = factory.Sequence(lambda n: n + 1)
    status = factory.Iterator(['Pending', 'In Progress', 'Completed'])
    replenishment_task = factory.SubFactory(VNATaskFactory,  status='Assigned')
    replenishment_task = None
    assigned_to = None  # Explicitly set to None, ensures no User assignment initially

    @factory.post_generation
    def post_create(self, create, extracted, **kwargs):
        if not create:
            return  # Avoid database operations if we're not creating an actual instance
        if kwargs.get('save', True):
            self.save() 
        
class ProductLocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductLocation
        django_get_or_create = ('product', 'location')  # Ensures uniqueness for 'product' and 'location'

    product = factory.SubFactory(FoodProductFactory)
    location = factory.SubFactory(LocationFactory)
    quantity = factory.Faker('random_int', min=0, max=1000)  # Generates a random quantity between 0 and 1000
    
class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order 
  

register(OrderFactory)

class OutboundFactory(LocationFactory):
    class Meta:
        model = Outbound
        skip_postgeneration_save=True

    address = factory.Faker('address')
    floor_number = factory.Sequence(lambda n: n % 5 + 1)
    bay_number = factory.Sequence(lambda n: (n % 10) + 1)
    additional_info = factory.Faker('sentence')
    location_identifier = factory.Sequence(lambda n: f"LOCID{n}")
    max_capacity = 500
    operational_restrictions = "None"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Adjust the arguments to pass to the superclass _create method
        # Ensure that the LocationFactory's _create method is called with the correct arguments
        return super()._create(model_class=model_class, *args, **kwargs)

class OrderPickingTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderPickingTask

    order = factory.SubFactory(OrderFactory)
    source_location = factory.SubFactory(LocationFactory)
    destination_location = factory.SubFactory(OutboundFactory)
    product = factory.SubFactory(FoodProductFactory)
    quantity = factory.Faker('random_number')
    vna_equipment = factory.Faker('word')
    start_time = factory.Faker('date_time_this_month')
    completion_time = factory.LazyAttribute(lambda o: o.start_time + timedelta(hours=2))
    status = factory.Iterator(['Pending', 'In Progress', 'Completed'])

register(OrderPickingTaskFactory)


class OrderPickingTaskFactory(DjangoModelFactory):
    class Meta:
        model = OrderPickingTask

    order = factory.SubFactory(OrderFactory)
    source_location = factory.SubFactory(LocationFactory)
    destination_location = factory.SubFactory(OutboundFactory)
    product = factory.SubFactory(FoodProductFactory)
    quantity = factory.Faker('random_int', min=1, max=100)
    vna_equipment = factory.Faker('bothify', text='VNA-####')
    status = factory.Iterator(['Pending', 'In Progress', 'Completed'])
    start_time = factory.LazyFunction(timezone.now)
    completion_time = factory.Maybe('completion_time', yes_declaration=factory.LazyFunction(timezone.now), no_declaration=None)

register(OrderPickingTaskFactory)

class ReplenishmentRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReplenishmentRequest

    product = factory.SubFactory(FoodProductFactory)  # Ensure this exists
    required_quantity = factory.Faker('random_int', min=10, max=1000)
    status = 'Requested'
    created_at = factory.LazyFunction(timezone.now)


register(ReplenishmentRequestFactory)

class ReplenishmentPickingTaskFactory(DjangoModelFactory):
    class Meta:
        model = ReplenishmentPickingTask

    replenishment_request = factory.SubFactory(ReplenishmentRequestFactory)
    product = factory.SubFactory(FoodProductFactory)
    source_location = factory.SubFactory(LocationFactory)
    destination_location = factory.SubFactory(PNDLocationFactory)
    quantity = factory.Faker('random_int', min=1, max=100)
    vna_equipment = factory.Faker('bothify', text='VNA-####')
    status = factory.Iterator(['Pending', 'In Progress', 'Completed'])
    start_time = factory.LazyFunction(timezone.now)
    completion_time = None

register(ReplenishmentPickingTaskFactory)

class PickFaceFactory(LocationFactory):
    class Meta:
        model = PickFace

    pick_face_code = factory.Sequence(lambda n: f"PF_{n:03d}")
    product = factory.SubFactory(FoodProductFactory)
    category = factory.SubFactory(CategoryFactory)
    current_stock = 100
    low_stock_threshold = 10
    target_stock_level = 150
    # Ensuring that inherited Location fields are initialized
    code = factory.Sequence(lambda n: f"LOC_{n:03d}")
    name = factory.Faker('word')
    level = factory.SubFactory(LevelFactory)  # Assume LevelFactory is defined
    side = factory.Iterator(['E', 'W', 'N', 'S'])
    location_number = factory.Sequence(lambda n: n)
    type = factory.Iterator(['Storage', 'PND', 'Pick Face'])
    status = factory.Iterator(['full', 'empty', 'low_stock'])
    
    @factory.post_generation
    def adjust_location_fields(self, create, extracted, **kwargs):
        if not create:
            return
        # Ensuring Location-specific fields are initialized
        self.type = 'Pick Face'
        self.save()


    @factory.post_generation
    def post_create(self, create, extracted, **kwargs):
        if not create:
            return
        # Applying additional settings if provided during instantiation
        if extracted:
            for key, value in extracted.items():
                setattr(self, key, value)
                
        # Check for calculate_needed_quantity references and replace them
        # (if necessary) with calculate_replenishment_quantity
        # For example:
        if hasattr(self, 'calculate_needed_quantity'):
            delattr(self, 'calculate_needed_quantity')

                
#STOCK LEVEL TEST MODEL
    
class StockLevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.StockLevel
        skip_postgeneration_save=True

    location = factory.SubFactory(LocationFactory)
    product = factory.SubFactory(FoodProductFactory)
    quantity = factory.Faker('random_number', digits=3)
    
    create_pick_face = factory.Trait(
        pick_face=factory.SubFactory(PickFaceFactory)
    )

    @factory.post_generation
    def post_create(self, create, extracted, **kwargs):
        if not create:
            return
        self.full_clean()  # Validate to ensure the object is correct
        self.save()

    @factory.post_generation
    def empty_stock(self, create, extracted, **kwargs):
        """Optionally set stock level to 0 after creation."""
        if extracted:  # Checking if `empty_stock=True` was passed when using the factory.
            self.quantity = 0
            if create:
                self.save() 

    
#LLOP TASK TEST MODEL

class LLOPTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LLOPTask
        skip_postgeneration_save=True

    task_type = factory.Iterator(['Picking', 'Replenishing'])
    product = factory.SubFactory(FoodProductFactory)
    source_location = factory.SubFactory(PickFaceFactory)
    destination_location = factory.SubFactory(OutboundFactory)
    quantity = factory.Faker('pyint', min_value=1, max_value=100)
    unit_price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    assigned_to = None
    status = 'Assigned'
    start_time = factory.LazyFunction(timezone.now)
    completion_time = None

    @factory.post_generation
    def setup_stock(self, create, extracted, **kwargs):
        if not create:
            return

        # Ensure source location has enough stock
        source_stock, _ = models.StockLevel.objects.get_or_create(
            location=self.source_location,
            product=self.product,
            defaults={'quantity': self.quantity + 50}  # Ensures sufficient stock
        )
        source_stock.quantity += self.quantity  # Simulate having more stock
        source_stock.save()

        # Ensure destination is ready to receive
        models.StockLevel.objects.get_or_create(
            location=self.destination_location,
            product=self.product,
            defaults={'quantity': 0}
        )

    



    






    


    







