from email.mime import application
import logging
from unittest.mock import patch
from django.forms import ValidationError
import pytest
import datetime
from decimal import Decimal
from django.utils import timezone
from channels.testing import WebsocketCommunicator
from warehouse.inventory.models import Address, Inbound, Level, Order, Outbound, PNDLocation, PickFace, PutawayTask, Supplier, VNATask
from warehouse.inventory import models
from warehouse.inventory.notification_utils import send_urgent_notification
from warehouse.tests.factories import AddressFactory, AisleFactory, CategoryFactory, CustomerFactory, FLTTaskFactory, FinalBayAssignmentFactory, FoodProductFactory, GatehouseBookingFactory, InboundFactory, LevelFactory, LocationFactory, OrderFactory, OrderItemFactory, OrderPickingTaskFactory, OutboundFactory, PNDLocationFactory, PickFaceFactory, ProductLocationFactory, ProvisionalBayAssignmentFactory, PutawayTaskFactory, RackFactory, ReceivingFactory, ReplenishmentPickingVNATaskFactory, ReplenishmentRequestFactory, ReplenishmentTaskFactory, StockLevelFactory, SupplierFactory, VNATaskFactory, ZoneFactory
from django.db.utils import IntegrityError
from asgiref.sync import sync_to_async
from warehouse.inventory.routing import application





@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, slug, is_active",
    [
        ("ambient food", "ambient-food", True),
        ("chilled food", "chilled-food", True),
        ("fresh", "fresh", True),
        ("frozen food", "frozen-food", True),
    ],
)
def test_inventory_category_creation(db, name, slug, is_active):
    # Directly create the category
    category = models.Category.objects.create(name=name, slug=slug, is_active=is_active)
    
    # Fetch the category to ensure it's saved and retrievable
    fetched_category = models.Category.objects.get(slug=slug)
    
    # Assert that the fetched category matches the created one
    assert fetched_category.name == name
    assert fetched_category.slug == slug
    assert fetched_category.is_active == is_active
    
@pytest.mark.django_db
@pytest.mark.parametrize(
    "street_number, street_name, city, county, country, post_code, is_valid",
    [
        ("100", "Oak Street", "Metropolis", "Metro", "USA", "10001", True),
        ("200", "Pine Street", "Gotham", "Gotham", "USA", "10002", True),
        ("300", "Maple Street", "Star City", "Star", "USA", "10003", True),
        ("400", "Cedar Street", "Central City", "Central", "USA", "10004", True),
        # Add an example of invalid data if there are any conditions under which creation should fail
        # For example, a duplicate post_code if that was a restriction.
        # ("500", "Elm Street", "Coast City", "Coast", "USA", "10001", False), # Assuming 10001 is not unique, based on your previous model unique constraints.
    ],
)
def test_address_creation_and_retrieval(street_number, street_name, city, county, country, post_code, is_valid):
    if is_valid:
        # Directly create the address
        address = Address.objects.create(
            street_number=street_number, 
            street_name=street_name, 
            city=city, 
            county=county, 
            country=country, 
            post_code=post_code
        )

        # Fetch the address to ensure it's saved and retrievable
        fetched_address = Address.objects.get(post_code=post_code)

        # Assert that the fetched address matches the created one
        assert fetched_address.street_number == street_number
        assert fetched_address.street_name == street_name
        assert fetched_address.city == city
        assert fetched_address.county == county
        assert fetched_address.country == country
        assert fetched_address.post_code == post_code
    else:
        # Test the creation of an address that violates some constraints (e.g., non-unique post_code)
        with pytest.raises(Exception):  # Use the specific exception that your model would raise under the failure condition
            Address.objects.create(
                street_number=street_number, 
                street_name=street_name, 
                city=city, 
                county=county, 
                country=country, 
                post_code=post_code
            )
            
@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, contact, email, contact_number, created_at, updated_at",
    [
        (
        "Supplier One",
        "John Doe",
        "johndoe@example.com",
        "123-456-7890",
        "2024-04-04T08:00:00Z",
        "2024-04-04T08:00:00Z",
        ),
        (
        "Supplier Two",
        "Jane Smith",
        "janesmith@example.com",
        "098-765-4321",
        "2024-04-04T08:00:00Z",
        "2024-04-04T08:00:00Z",
        ),
    ],
)
def test_supplier_creation_with_address(name, contact, email, contact_number, created_at, updated_at):
    # Create an Address instance
    address = AddressFactory.create()

    # Create a Supplier instance using the address and parameterized values
    supplier = SupplierFactory.create(
        name=name,
        contact=contact,
        email=email,
        contact_number=contact_number,
        address=address
    )

    # Fetch the supplier to ensure it's saved and retrievable
    fetched_supplier = Supplier.objects.get(name=supplier.name)

    # Assert that the fetched supplier matches the created one
    assert fetched_supplier.name == name
    assert fetched_supplier.contact == contact
    assert fetched_supplier.email == email
    assert fetched_supplier.contact_number == contact_number
    assert fetched_supplier.address == address

    # Since the `created_at` and `updated_at` fields are auto-handled by Django,
    # and this test doesn't directly utilize them, they can be omitted or handled differently.
  
@pytest.mark.django_db
def test_food_product_creation():
    # Set up data for a single test case.
    sku = "SKU00001"
    name = "Product One"
    description = "Description for product one"
    quantity = 100
    unit_price = Decimal("9.99")
    expiration_date = datetime.datetime.strptime("2025-04-04", "%Y-%m-%d").date()
    category_name = "Category One"
    suppliers_data = [
        {"name": "Supplier One", "contact": "John Doe", "email": "johndoe@example.com", "contact_number": "123-456-7890"},
        {"name": "Supplier Two", "contact": "Jane Smith", "email": "janesmith@example.com", "contact_number": "098-765-4321"},
    ]

    # Create Category instance.
    category = CategoryFactory.create(name=category_name)

    # Create FoodProduct instance using the created category.
    food_product = FoodProductFactory.create(
    sku=sku,
    name=name,
    description=description,
    quantity=quantity,
    unit_price=unit_price,
    expiration_date=expiration_date,
    date_received=timezone.now().date(),  # Ensure this matches your model's requirements
    category=category
)
    print("Test Debug - Quantity:", food_product.quantity, "Date Received:", food_product.date_received)
    
    print("DEBUG in Test:", food_product.quantity, food_product.date_received)
    
     # Assume you are now going to use food_product in a way that has previously failed:
    try:
        food_product.save()  # This is where you might be catching IntegrityErrors.
    except IntegrityError as e:
        print("Error during save:", e)
        raise

    # Further assertions or usage of food_product
    assert food_product.quantity is not None
    # Create Supplier instances and add to FoodProduct.
    for supplier_data in suppliers_data:
        supplier = SupplierFactory.create(**supplier_data)
        food_product.suppliers.add(supplier)

    # Refresh the FoodProduct from the database to make sure we have all related objects.
    food_product.refresh_from_db()

    # Assert that the created FoodProduct matches expectations.
    assert food_product.name == name
    assert food_product.description == description
    assert food_product.quantity == quantity
    assert food_product.unit_price == unit_price
    assert food_product.expiration_date == expiration_date
    assert food_product.category.name == category_name
    assert set(supplier['name'] for supplier in suppliers_data) == set(supplier.name for supplier in food_product.suppliers.all())
    assert food_product.suppliers.count() == len(suppliers_data)
    assert food_product.quantity is not None, f"Expected quantity to be set but got None"
    assert food_product.date_received is not None, f"Expected date_received to be set but got None"
    

    

@pytest.mark.django_db
@pytest.mark.parametrize(
    "sku, name, description, quantity, unit_price, expiration_date, category_name, suppliers_data, receiving_data",
    [
        (
            "SKU00001",
            "Product One",
            "Description for product one",
            100,
            "9.99",
            "2025-04-04",
            "Category One",
            [
                {"name": "Supplier One", "contact": "John Doe", "email": "johndoe@example.com", "contact_number": "123-456-7890"},
                {"name": "Supplier Two", "contact": "Jane Smith", "email": "janesmith@example.com", "contact_number": "098-765-4321"},
            ],
            {
                "quantity": 50,
                "receiving_date": "2024-04-04",
                "notes": "Initial batch",
            },
        ),
    ],
)
def test_receiving_creation(
    sku, name, description, quantity, unit_price, expiration_date, category_name, suppliers_data, receiving_data
):
    # Create Category instance
    category = CategoryFactory.create(name=category_name)

    # Create FoodProduct instance including date_received
    food_product = FoodProductFactory.create(
        sku=sku,
        name=name,
        description=description,
        quantity=quantity,
        unit_price=Decimal(unit_price),
        expiration_date=datetime.datetime.strptime(expiration_date, "%Y-%m-%d").date(),
        date_received=datetime.datetime.strptime(receiving_data['receiving_date'], "%Y-%m-%d").date(),
        category=category
    )

    # Create Supplier instances and add to FoodProduct
    for supplier_data in suppliers_data:
        supplier = SupplierFactory.create(**supplier_data)
        food_product.suppliers.add(supplier)

    # Creating the receiving
    receiving = ReceivingFactory.create(
        product=food_product,
        quantity=receiving_data['quantity'],
        receiving_date=datetime.datetime.strptime(receiving_data['receiving_date'], "%Y-%m-%d").date(),
        notes=receiving_data['notes']
    )

    # Assertions
    assert receiving.product == food_product
    assert receiving.quantity == receiving_data['quantity']
    assert receiving.receiving_date == datetime.datetime.strptime(receiving_data['receiving_date'], "%Y-%m-%d").date()
    assert receiving.notes == receiving_data['notes']

    
@pytest.mark.django_db
@pytest.mark.parametrize(
    "gatehouse_info, provisional_info, final_info",
    [
        ({
            "driver_name": "John Doe",
            "company": "Doe Transport",
            "vehicle_registration": "ABC123",
            "trailer_number": "TN1234",
            "arrival_time": timezone.now(),
            "paperwork": "path/to/paperwork.pdf",
         },
         {
            "provisional_bay": "Provisional Bay 1",
         },
         {
            "final_bay": "Final Bay 1",
         })
    ]
)
def test_gatehouse_to_final_assignment_process(gatehouse_info, provisional_info, final_info):
    # Create GatehouseBooking instance
    gatehouse_booking = GatehouseBookingFactory(**gatehouse_info)

    # Assert GatehouseBooking instance attributes
    assert gatehouse_booking.driver_name == gatehouse_info["driver_name"]
    assert gatehouse_booking.company == gatehouse_info["company"]
    assert gatehouse_booking.vehicle_registration == gatehouse_info["vehicle_registration"]
    assert gatehouse_booking.trailer_number == gatehouse_info["trailer_number"]
    assert gatehouse_booking.arrival_time.strftime('%Y-%m-%d %H:%M') == gatehouse_info["arrival_time"].strftime('%Y-%m-%d %H:%M')
    # Assuming paperwork is a FileField and you're testing for its existence rather than equality
    assert gatehouse_booking.paperwork.name is not None

    # Create ProvisionalBayAssignment linked to the GatehouseBooking
    provisional_bay_assignment = ProvisionalBayAssignmentFactory(
        gatehouse_booking=gatehouse_booking,
        provisional_bay=provisional_info["provisional_bay"]
    )

    # Assert ProvisionalBayAssignment instance attributes and relationships
    assert provisional_bay_assignment.gatehouse_booking == gatehouse_booking
    assert provisional_bay_assignment.provisional_bay == provisional_info["provisional_bay"]
    # Assert reverse relationship if applicable
    assert gatehouse_booking.provisionalbayassignment == provisional_bay_assignment

    # Create FinalBayAssignment linked to the ProvisionalBayAssignment
    final_bay_assignment = FinalBayAssignmentFactory(
        provisional_bay_assignment=provisional_bay_assignment,
        final_bay=final_info["final_bay"]
    )

    # Assert FinalBayAssignment instance attributes and relationships
    assert final_bay_assignment.provisional_bay_assignment == provisional_bay_assignment
    assert final_bay_assignment.final_bay == final_info["final_bay"]
    # Assert reverse relationship if applicable
    assert provisional_bay_assignment.finalbayassignment == final_bay_assignment

    # Assert that the entire chain of relationships is coherent
    assert final_bay_assignment.provisional_bay_assignment.gatehouse_booking == gatehouse_booking
    
@pytest.fixture
@pytest.mark.django_db
def pnd_location():
    return PNDLocationFactory()

@pytest.fixture
@pytest.mark.django_db
def inbound():
    final_bay_assignment = FinalBayAssignmentFactory()
    product = FoodProductFactory()
    return InboundFactory(final_bay_assignment=final_bay_assignment, product=product)

@pytest.fixture
@pytest.mark.django_db
def putaway_task(inbound, pnd_location):
    return PutawayTaskFactory(inbound=inbound, pnd_location=pnd_location)

@pytest.mark.django_db
def test_putaway_workflow():
    # Create necessary instances with all required fields
    category = CategoryFactory.create()
    product = FoodProductFactory(
        category=category,
        quantity=100,  # Specific quantity
        unit_price=Decimal("10.99"),
        date_received=timezone.now().date(),
        expiration_date=timezone.now().date() + timezone.timedelta(days=365)
    )

    # Creating a PND location using the correct factory fields
    pnd_location = PNDLocationFactory.create()

    # Creating Inbound and PutawayTask instances
    inbound = InboundFactory.create(product=product)
    putaway_task = PutawayTaskFactory.create(
        inbound=inbound, 
        pnd_location=pnd_location, 
        status="Assigned"
    )

    # Assertions to validate the workflow logic
    assert PNDLocation.objects.count() == 1, "There should be exactly one PND location."
    assert Inbound.objects.count() == 1, "There should be exactly one inbound record."
    assert PutawayTask.objects.count() == 1, "There should be exactly one putaway task."

    putaway_task_record = PutawayTask.objects.first()
    assert putaway_task_record.inbound == inbound, "The putaway task's inbound should match the created inbound."
    assert putaway_task_record.pnd_location == pnd_location, "The putaway task's PND location should be set correctly."
    assert putaway_task_record.status == "Assigned", "The status of the putaway task should be 'Assigned'."
    assert isinstance(putaway_task_record.pnd_location, PNDLocation), "pnd_location must be an instance of PNDLocation"

    
    
@pytest.mark.django_db
def test_that_putaway_task_is_created_for_received_inbound():
    # Create a PNDLocation instance.
    pnd_location = PNDLocationFactory()
    
    # Ensure that the product linked to the Inbound record has a category
    # with the necessary PND location to trigger the signal correctly.
    category = CategoryFactory(pnd_location=pnd_location)
    inbound_record = InboundFactory(status='Received', product__category=category)

    # Saving the Inbound record should trigger the signal.
    # Verify that a PutawayTask has been created as expected.
    assert PutawayTask.objects.filter(inbound=inbound_record).exists(), \
        "The PutawayTask was not created for the Inbound record with status 'Received'."
        
@pytest.mark.django_db
def test_handle_inbound_received_signal():
    # Use the InboundFactory to create an inbound record with the status 'Received'
    inbound = InboundFactory(status='Received', receiving_date=timezone.now())

    # Save the inbound record to trigger the signal
    inbound.save()

    # Assert that a PutawayTask was created for the inbound record
    putaway_task_exists = PutawayTask.objects.filter(inbound=inbound).exists()
    assert putaway_task_exists, "PutawayTask was not created for the received inbound record" 
    
@pytest.mark.django_db
@pytest.mark.parametrize("status, expected_weight", [
    ("empty", 0),
    ("full", 18),
    # Add more status and expected_weight pairs as needed
])
def test_location_creation_with_various_statuses(status, expected_weight):
    # Create a zone, aisle, rack, and level to ensure the location has all necessary relations
    zone = ZoneFactory()
    aisle = AisleFactory(zone=zone)
    rack = RackFactory(aisle=aisle)
    level = LevelFactory(rack=rack)
    
    # Create a location with the specified status and a weight that should be aligned with the status
    location = LocationFactory(level=level, status=status, weight=expected_weight)
    
    # Fetch the location from the database to ensure it's saved and retrievable
    fetched_location = location.__class__.objects.get(id=location.id)
    
    # Verify the location's attributes
    assert fetched_location.status == status
    assert fetched_location.weight == expected_weight
    # Verify the location's relationships
    assert fetched_location.level == level
    assert fetched_location.level.rack == rack
    assert fetched_location.level.rack.aisle == aisle
    assert fetched_location.level.rack.aisle.zone == zone     
        
@pytest.mark.django_db
def test_location_update_signal_triggers_notifications():
    location = LocationFactory(status='empty', weight=0.00)

    # Make sure the mock path matches where the `send_email_notification` function is imported and called.
    # If the function is called as a result of status changes in the `location` object, ensure the mock path reflects that.
    with patch('warehouse.inventory.notification_utils.send_email_notification') as mock_send_email:
        # Assuming `update_status_based_on_sensor_data` is a method of `location` that might change its status based on the weight
        location.update_status_based_on_sensor_data(5.00)

        # Directly checking the status after the method call to determine if an email should have been sent
        if location.status == 'vor':
            expected_message = f"Verification required for location {location.id}"
            mock_send_email.assert_called_once_with(
                "Verification Required Notification", 
                expected_message, 
                "recipient@example.com"
            )
        else:
            mock_send_email.assert_not_called()
        
@pytest.mark.django_db
def test_location_urgent_pick_triggers_notification():
    # Assuming 'urgent_pick' is a valid status in your model that triggers an urgent notification
    location = LocationFactory(status='urgent_pick', weight=5.00)

    # Ensure the mock path is correct; it should match exactly where send_email_notification is imported and used
    with patch('warehouse.inventory.notification_utils.send_email_notification') as mock_send_email:
        # Directly call the high-level notification function with the prepared location
        send_urgent_notification(location)
        
        # Verify that send_email_notification was called correctly
        mock_send_email.assert_called_once_with(
            "Urgent Picking Notification", 
            f"Urgent picking required for location {location.id}", 
            "recipient@example.com"
        )

        
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_vnatask_creation_and_notification():
    # Setup test data using factories
    pnd_location = await sync_to_async(LocationFactory)(type='PND')
    
    # Create a category instance first
    category = await sync_to_async(CategoryFactory)()

    # Ensure product has all required fields including a non-null expiration date and a valid category
    product = await sync_to_async(FoodProductFactory)(
        category=category,
        quantity=100,
        unit_price=Decimal("10.99"),
        date_received=timezone.now().date(),
        expiration_date=timezone.now().date() + datetime.timedelta(days=365)  # Set an expiration date one year from now
    )

    destination_location = await sync_to_async(LocationFactory)(type='Storage')

    # Create VNA Task instance
    vna_task = await sync_to_async(VNATaskFactory)(
        task_type='Putaway',
        source_location=pnd_location,
        destination_location=destination_location,
        product=product,
        status='Assigned'  # Explicitly set status to ensure test consistency
    )

    # Validation of task setup
    assert vna_task.source_location.type == 'PND', "Source location must be PND for Putaway tasks"
    assert vna_task.destination_location == destination_location, "Destination location must match the expected location"
    assert vna_task.product == product, "Product must match the expected product"
    assert vna_task.status == 'Assigned', "Task status should initially be 'Assigned'"

    # Setup WebSocket communicator on the appropriate route
    communicator = WebsocketCommunicator(application, "/ws/vna_tasks/")
    connected, _ = await communicator.connect()
    assert connected, "WebSocket connection should be established"

    # Send a JSON message to the connected WebSocket
    await communicator.send_json_to({
        "type": "request_task_info",
        "task_id": str(vna_task.id)
    })

    # Receive response from WebSocket
    response = await communicator.receive_json_from()
    assert response.get("type") == "new_task", "Response type should be 'new_task'"
    assert response.get("task_id") == str(vna_task.id), "Task ID should match the one requested"

    # Clean up after test
    await communicator.disconnect()
    
@pytest.fixture
@pytest.mark.django_db
def customer_factory():
    def create_customer(**kwargs):
        return CustomerFactory(**kwargs)
    return create_customer


    
@pytest.mark.django_db
def test_create_order(customer_factory):  # Inject the customer_factory fixture
    customer = customer_factory()  # Create a customer instance
    order = OrderFactory(customer=customer)  # Associate the order with the customer
    assert order.customer is not None
    assert order.status == 'Pending'

@pytest.mark.django_db
def test_create_order_item():
    order_item = OrderItemFactory()
    assert order_item.order is not None
    assert order_item.total_price == order_item.quantity * order_item.unit_price
    
@pytest.mark.django_db
def test_stock_level_creation():
    # Standard creation without specifying 'create_pick_face'; it will be randomly determined by the factory.
    stock_level = StockLevelFactory()
    assert 0 <= stock_level.quantity <= 1000, "Quantity should be within the valid range"
    
# STOCK LEVEL TEST

@pytest.mark.django_db
def test_stock_level_creation_with_pick_face():
    # Creating with a guaranteed PickFace
    stock_level = StockLevelFactory(create_pick_face=True)
    assert stock_level.pick_face is not None, "PickFace should be assigned"

@pytest.mark.django_db
def test_stock_level_creation_without_pick_face():
    # Creating without a PickFace
    stock_level = StockLevelFactory(create_pick_face=False)
    assert stock_level.pick_face is None, "PickFace should not be assigned"

@pytest.mark.django_db
def test_stock_level_creation_empty_stock():
    # Test with stock explicitly set to 0
    stock_level = StockLevelFactory(empty_stock=True)
    assert stock_level.quantity == 0, "Stock level should be set to 0"
    

@pytest.mark.django_db
def test_replenishment_task_high_priority():
    # Create a category instance for the food product
    category = CategoryFactory.create()

    # Creating a high demand product with all required fields explicitly set
    high_demand_product = FoodProductFactory(
        category=category,  # Associating the category
        quantity=150,  # Explicitly set a high quantity for high demand
        unit_price=Decimal('20.99'),  # Assuming a realistic unit price is necessary
        date_received=timezone.now().date(),  # Ensure this is not None
        expiration_date=timezone.now().date() + timezone.timedelta(days=365),  # Provide a future expiration date
        is_high_demand=True
    )
    
    # Creating a replenishment task with a high demand product and quantity
    replenishment_task_high_priority = ReplenishmentTaskFactory(
        product=high_demand_product,
        quantity=101  # This quantity should trigger a high priority
    )
    
    # Print statements for debugging purposes
    print("Product Quantity:", high_demand_product.quantity)
    print("Task Quantity:", replenishment_task_high_priority.quantity)
    print("Priority:", replenishment_task_high_priority.priority)

    # Asserting that the priority is set to high
    assert replenishment_task_high_priority.priority == 100, "Priority should be 100 for high demand products or quantity > 100"

@pytest.mark.django_db
def test_replenishment_task_normal_priority():
    # Create a category instance for the food product
    category = CategoryFactory.create()

    # Creating a normal demand product with all required fields explicitly set
    normal_demand_product = FoodProductFactory(
        category=category,  # Associating the category
        quantity=100,
        unit_price=Decimal('15.99'),  # Assuming a realistic unit price is necessary
        date_received=timezone.now().date(),  # Ensure this is not None
        expiration_date=timezone.now().date() + timezone.timedelta(days=365),  # Provide a future expiration date
        is_high_demand=False
    )
    
    # Ensure the quantity leads to a 'normal' priority according to your business rules
    replenishment_task_normal_priority = ReplenishmentTaskFactory(
        product=normal_demand_product,
        quantity=50  # Assuming this triggers 'normal' priority
    )
    
    # Print statements for debugging purposes
    print("Product Quantity:", normal_demand_product.quantity)
    print("Task Quantity:", replenishment_task_normal_priority.quantity)
    print("Priority:", replenishment_task_normal_priority.priority)

    # Asserting that the priority is set to normal
    assert replenishment_task_normal_priority.priority == 10, "Priority should be 10 for normal demand products with quantity <= 100"
    
@pytest.mark.django_db
def test_flt_task_creation():
    flt_task = FLTTaskFactory()
    assert flt_task.status == 'Pending', "The default status should be 'Pending'"
    assert 1 <= flt_task.quantity <= 500, "Quantity should be within the specified range"
    assert flt_task.assigned_to is None, "No user should be assigned to the FLT Task"
    
@pytest.mark.django_db
def test_product_location_str():
    product_location = ProductLocationFactory()
    expected_str = f"{product_location.product.name} at {product_location.location}"
    assert str(product_location) == expected_str, "The __str__ method should return the correct string representation"
    


@pytest.mark.django_db
def test_order_picking_task():
    # Create necessary instances with all required fields properly initialized
    product = FoodProductFactory.create(
        quantity=150,  # Set a realistic positive quantity
        unit_price=Decimal("20.00"),  # Ensure a non-null unit price
        date_received=timezone.now().date(),  # Assume a received date
        expiration_date=timezone.now().date() + timezone.timedelta(days=365)  # Set an expiration date
    )
    customer = CustomerFactory.create()
    order = OrderFactory.create(customer=customer, order_date=timezone.now())
    storage_location = LocationFactory.create(type='Storage')
    pnd_location = LocationFactory.create(type='PND')

    # Create an Order Picking task with explicitly set parameters
    order_picking_task = OrderPickingTaskFactory.create(
        order=order,
        product=product,
        source_location=storage_location,
        destination_location=pnd_location,
        quantity=50,  # Explicitly set the quantity involved in the task
        vna_equipment="VNA-1234",
        status='Pending',
        start_time=timezone.now(),
        completion_time=None  # Explicitly setting completion time to None
    )

    # Assertions to ensure the task is set up correctly
    assert order_picking_task.product == product, "The product should be correctly assigned to the task."
    assert order_picking_task.source_location == storage_location, "Source location should be correctly assigned."
    assert order_picking_task.destination_location == pnd_location, "Destination location should be correctly assigned."
    assert order_picking_task.quantity == 50, "Task quantity should be correctly set."
    assert order_picking_task.vna_equipment == "VNA-1234", "VNA equipment should be correctly set."
    assert order_picking_task.status == 'Pending', "Task status should be 'Pending'."
    assert order_picking_task.start_time <= timezone.now(), "Start time should be now or earlier."
    assert order_picking_task.completion_time is None, "Completion time should be None for an incomplete task."

    # Check the string representation
    expected_str = f"{order_picking_task.product.name} from {order_picking_task.source_location} to {order_picking_task.destination_location} [{order_picking_task.status}]"
    assert str(order_picking_task) == expected_str, "String representation should be formatted correctly."


@pytest.mark.django_db
def test_replenishment_picking_task(replenishment_picking_task_factory):
    task = replenishment_picking_task_factory()

    # Assert the correctness of each field
    assert task.replenishment_request is not None
    assert task.product is not None
    assert task.source_location is not None
    assert task.destination_location is not None
    assert 1 <= task.quantity <= 100
    assert task.vna_equipment.startswith('VNA-')
    assert task.status in ['Pending', 'In Progress', 'Completed']
    assert task.start_time <= timezone.now()
    assert task.completion_time is None or task.start_time <= task.completion_time

    # Check the string representation
    expected_str = f"{task.product.name} from {task.source_location} to {task.destination_location} [{task.status}]"
    assert str(task) == expected_str

@pytest.mark.django_db
def test_replenishment_request():
    # Create a Category instance to fulfill foreign key requirements for the product
    category = CategoryFactory.create()

    # Ensure that the product is created with all non-nullable fields properly filled
    product = FoodProductFactory.create(
        name="Test Product",
        category=category,
        quantity=1000,  # Ensure this is set to a realistic positive quantity
        unit_price=Decimal("15.99"),  # Set a non-null unit price
        date_received=timezone.now().date() - timezone.timedelta(days=30),  # Ensure a received date is set
        expiration_date=timezone.now().date() + timezone.timedelta(days=180)  # Set a non-null and valid expiration date
    )

    # Create a Replenishment Request for the product
    request = ReplenishmentRequestFactory.create(
        product=product,
        required_quantity=757,
        status='Requested',  # Explicitly setting to check default behavior override if needed
        created_at=timezone.now()
    )

    # Assertions to validate the setup and field correctness
    assert request.product == product, "The product associated with the request should match the created product."
    assert request.required_quantity == 757, "The required quantity should match the specified value."
    assert request.status == 'Requested', "The status of the replenishment request should be 'Requested'."
    assert request.created_at <= timezone.now(), "The creation time of the request should be now or earlier."

    # Check the string representation to match expectations
    expected_str = f"Replenishment request for {request.product.name}, Quantity: {request.required_quantity}"
    assert str(request) == expected_str, "The string representation of the request should be formatted correctly."
    
@pytest.mark.django_db
@pytest.mark.parametrize("task_type, source_type, dest_type", [
    ('Putaway', 'PND', 'Storage'),
    ('Order Picking', 'Storage', 'PND'),
    ('Replenishment Picking', 'Storage', 'PND')
])
def test_vna_task_types(task_type, source_type, dest_type):
    # Creating source and destination locations using the specified types
    source_location = LocationFactory(type=source_type)
    destination_location = LocationFactory(type=dest_type)

    # Creating a VNATask using the above locations and checking initial conditions
    task = VNATaskFactory(
        task_type=task_type,
        source_location=source_location,
        destination_location=destination_location
    )
    
    # Assertions to verify the task has been created with the correct attributes
    assert task.source_location.type == source_type, f"Source location type mismatch: expected {source_type}, got {task.source_location.type}"
    assert task.destination_location.type == dest_type, f"Destination location type mismatch: expected {dest_type}, got {task.destination_location.type}"
    assert task.task_type == task_type, f"Task type mismatch: expected {task_type}, got {task.task_type}"

    # Changing the task status to 'Completed' and saving the changes
    task.status = 'Completed'
    task.save()

    # Asserting that the task status update is persisted correctly
    assert VNATask.objects.filter(id=task.id, status='Completed').exists(), "Task status was not updated to 'Completed' as expected."
    
@pytest.mark.django_db    
@pytest.mark.parametrize("task_type,source_type,dest_type", [
    ('Putaway', 'PND', 'Storage'),
    ('Order Picking', 'Storage', 'PND'),
    ('Replenishment Picking', 'Storage', 'PND')
])
def test_vna_task_types(task_type, source_type, dest_type):
    source_location = LocationFactory(type=source_type)
    destination_location = LocationFactory(type=dest_type)
    task = VNATaskFactory(
        task_type=task_type,
        source_location=source_location,
        destination_location=destination_location
    )
    
@pytest.mark.django_db
def test_order_picking_task(order_picking_task_factory, customer_factory):
    # Create a customer instance
    customer = customer_factory.create()
    
    # Create an Order instance associated with the customer
    order = Order.objects.create(customer=customer, order_date=timezone.now())
    
    # Define locations
    source_location = LocationFactory.create()
    destination_location = OutboundFactory.create(floor_number=1)
    
    # Ensure product has all required fields set, especially `quantity`
    product = FoodProductFactory.create(
        quantity=10,  # Explicitly setting quantity to a valid number
        unit_price=Decimal("19.99"),  # Assuming unit_price is also required
        date_received=timezone.now().date(),  # Set required date fields if not handled by factory
        expiration_date=timezone.now().date() + datetime.timedelta(days=365),
        category=CategoryFactory.create()  # Ensure a category is assigned if required
    )
    
    # Create an Order Picking task
    task = order_picking_task_factory.create(
        order=order,
        source_location=source_location,
        destination_location=destination_location,
        product=product,
        quantity=10,  # This should match or relate logically to product's quantity if checked
        vna_equipment="VNA-1234",
        start_time=timezone.now(),
        status='Pending'
    )

    # Assertions to ensure the task is set up correctly
    assert isinstance(task.destination_location, Outbound), "Destination location must be an instance of Outbound"
    assert task.destination_location.floor_number == 1, "Floor number must match the specified value"
    assert task.product == product, "The task's product should correctly reference the created product instance"
    assert task.quantity == 10, "The task's quantity should be correctly set to 10"
    assert task.status == 'Pending', "Initial status should be 'Pending'"

    
@pytest.fixture(autouse=True)
def setup_default_locations(db):
    if not Outbound.objects.exists():
        Outbound.objects.create(name="Default Outbound", address="Default Address")
    
@pytest.mark.django_db
def test_flt_task_logic():
    # Create a Category instance to ensure foreign key requirements are met
    category = CategoryFactory.create()

    # Create necessary objects using factories ensuring all fields, especially 'quantity', are populated
    product = FoodProductFactory.create(
        category=category,
        quantity=100,  # Explicitly set a valid quantity to avoid IntegrityError
        unit_price=Decimal("20.00"),  # Ensure a unit price is set
        expiration_date=timezone.now().date() + timezone.timedelta(days=365),  # Set a future expiration date
        date_received=timezone.now().date() - timezone.timedelta(days=10)  # Set a received date in the past
    )

    # Define locations for the FLT task
    source_location = LocationFactory.create()
    destination_location = LocationFactory.create()

    # Create a VNA Task with a specific quantity
    vna_quantity = 50
    vna_task = VNATaskFactory.create(
        task_type='Replenishment Picking',
        product=product,
        quantity=vna_quantity,  # Assigning a specific quantity for the VNA task
        source_location=source_location,
        destination_location=destination_location,
        status='Assigned'
    )

    # Create FLT Task with the same quantity as the VNA Task to ensure they match
    flt_task = FLTTaskFactory.create(  # Changed to create() to actually save and better test real conditions
        product=product,
        source_location=source_location,
        destination_location=destination_location,
        vna_task=vna_task,
        replenishment_task=None,  # Explicitly setting to None if it's a valid scenario
        quantity=vna_quantity  # Ensure this quantity matches the VNA task's quantity
    )

    # Assertions to validate the task setup
    assert flt_task.product == product, "FLT task product should match the created product"
    assert flt_task.vna_task == vna_task, "FLT task should correctly reference the VNA task"
    assert flt_task.replenishment_task is None, "Replenishment task should explicitly be None if intended"
    assert flt_task.quantity == vna_task.quantity, "FLT task quantity should be correctly set and match the VNA task quantity"

    
@pytest.mark.django_db
def test_location_creation():
    location = LocationFactory(
        level__rack__aisle__zone__name="Test Zone",
        level__rack__aisle__aisle_letter="A",
        level__rack__rack_number="1",
        level__level='G',
        side='E',
        location_number=1,
        weight=20.00,
        type='Storage',
        status='full',
        name='Location 1'
    )
    assert location.__str__() == "Location 1 (East) on Ground Floor in Rack 1, Aisle A"
    
# PICKFACE TEST MODEL

@pytest.mark.django_db
class TestPickFaceModel:
    def test_pickface_creation(self):
        pick_face = PickFaceFactory()
        assert pick_face.code.startswith('PF_')
        assert pick_face.current_stock == 50
        assert pick_face.low_stock_threshold == 10
        assert pick_face.target_stock_level == 100

    def test_pickface_stock_thresholds(self):
        pick_face = PickFaceFactory(current_stock=5)
        assert pick_face.current_stock < pick_face.low_stock_threshold, "Stock should be below threshold"

    def test_pickface_string_representation(self):
        pick_face = PickFaceFactory()
        expected_representation = f"{pick_face.code} - {pick_face.location.name} ({pick_face.location.get_side_display()}) - {pick_face.category.name}"
        assert str(pick_face) == expected_representation

    def test_adjusting_stock_levels(self):
        # Test adjusting stock levels above and below thresholds
        pnd_location = PNDLocationFactory.create()  # Ensure this factory correctly sets the location_type to 'PND'

        pick_face = PickFaceFactory(current_stock=5, location=pnd_location)
        pick_face.current_stock = 15  # Adjust stock above the threshold
        assert pick_face.current_stock > pick_face.low_stock_threshold, "Stock should now be above threshold"

        pick_face.current_stock = 3  # Adjust stock below the threshold again
        assert pick_face.current_stock < pick_face.low_stock_threshold, "Stock should again be below threshold"

    def test_negative_current_stock(self):
        # Attempt to create a PickFace with negative current_stock and validate error
        pick_face = PickFaceFactory.build(current_stock=-1)
        with pytest.raises(ValidationError):
            pick_face.full_clean()  # This explicitly calls clean() among other checks

    def test_pickface_stock_adjustments(self):
        # Tests both increasing and decreasing stock relative to thresholds
        pick_face = PickFaceFactory(current_stock=5)  # Start below the low stock threshold
        assert pick_face.current_stock < pick_face.low_stock_threshold

        pick_face.current_stock += 10  # Increase stock
        pick_face.save()
        assert pick_face.current_stock > pick_face.low_stock_threshold  # Now should be above

        pick_face.current_stock -= 12  # Decrease stock to below original threshold
        pick_face.save()
        assert pick_face.current_stock < pick_face.low_stock_threshold
        
@pytest.fixture
def pick_face_factory():
    def create(**kwargs):
        return PickFace(**kwargs)
    return create

@pytest.mark.django_db
def test_stock_level_creation_with_pick_face():
    stock_level = StockLevelFactory(create_pick_face=True)
    assert stock_level.pick_face is not None
    assert 0 <= stock_level.quantity <= 1000

@pytest.mark.django_db
def test_stock_level_creation_without_pick_face():
    stock_level = StockLevelFactory(create_pick_face=False)
    assert stock_level.pick_face is None
    assert 0 <= stock_level.quantity <= 1000

@pytest.mark.django_db
def test_stock_level_creation_empty_stock():
    stock_level = StockLevelFactory(empty_stock=True)
    assert stock_level.quantity == 0            
    
#VNA TEST MODEL FOR TASKS

@pytest.mark.django_db
def test_order_picking_task_creation():
    # Create a Category instance to fulfill the foreign key requirement for the product
    category = CategoryFactory.create()

    # Create necessary objects using factories ensuring all fields, especially 'unit_price', are populated
    product = FoodProductFactory(
        name="Test1 Product",
        category=category,
        quantity=100,  # Explicitly set a valid quantity
        unit_price=Decimal("15.75"),  # Explicitly set a valid unit price to avoid IntegrityError
        expiration_date=timezone.now().date() + timezone.timedelta(days=365),  # Set a future expiration date
        date_received=timezone.now().date() - timezone.timedelta(days=5)  # Set a received date in the past
    )

    # Define locations for the picking task
    storage_location = LocationFactory.create(type='Storage', side='W', location_number=101)
    destination_location = LocationFactory.create(type='PND', side='E', location_number=100)

    # Create an Order Picking task
    order_picking_task = VNATaskFactory.create(
        task_type='Order Picking',
        product=product,
        source_location=storage_location,
        destination_location=destination_location,
        quantity=50  # Setting task-specific quantity
    )

    # Assertions to validate the setup
    
    assert order_picking_task.task_type == 'Order Picking'
    assert order_picking_task.product == product
    assert order_picking_task.source_location == storage_location
    assert order_picking_task.destination_location == destination_location
    assert order_picking_task.quantity == 50, "Task quantity should match the specified value"
    
@pytest.mark.django_db
def test_putaway_task_creation():
    # Create a Category instance to satisfy the category foreign key requirement
    category = CategoryFactory.create()

    # Create necessary objects using factories ensuring all fields, especially 'quantity', are populated
    product = FoodProductFactory(
        category=category,
        quantity=150,  # Explicitly set a valid quantity
        unit_price=Decimal("20.99"),  # Ensure unit price is set
        expiration_date=timezone.now().date() + timezone.timedelta(days=365), # Set a future expiration date
        date_received=timezone.now().date() - timezone.timedelta(days=10)  # Set a received date in the past
    )

    # Locations for the task
    pnd_location = LocationFactory.create(type='PND', side='E', location_number=100)
    storage_location = LocationFactory.create(type='Storage', side='W', location_number=101)

    # Create a Putaway task with the product
    putaway_task = VNATaskFactory.create(
        task_type='Putaway',
        product=product,
        source_location=pnd_location,
        destination_location=storage_location,
    )

    # Assertions to validate the setup
    assert putaway_task.task_type == 'Putaway'
    assert putaway_task.product == product
    assert putaway_task.source_location == pnd_location
    assert putaway_task.destination_location == storage_location
    assert putaway_task.product.quantity == 150, "Product quantity should be correctly set and retrieved"
    
@pytest.mark.django_db
def test_replenish_task_creation():
    # Ensure all required fields for FoodProduct are correctly populated
    category = CategoryFactory.create()
    product = FoodProductFactory(
        quantity=150,
        unit_price=Decimal("29.99"),
        date_received=timezone.now().date(),
        expiration_date=timezone.now().date() + timezone.timedelta(days=365),
        category=category  # Explicitly set category
    )

    storage_location = LocationFactory(type='Storage', side='W', location_number=101)
    pnd_location = LocationFactory(type='PND', side='E', location_number=102)

    replenish_task = ReplenishmentPickingVNATaskFactory.create(
        product=product,
        source_location=storage_location,
        destination_location=pnd_location,
        task_type='Replenishment Picking'
    )

    # Assertions to validate the setup
    assert replenish_task.product == product
    assert replenish_task.product.category_id is not None, "Category ID should not be None"
    assert replenish_task.source_location == storage_location
    assert replenish_task.destination_location == pnd_location



# FLT TEST MODEL

@pytest.mark.django_db
def test_flt_task_creation():
    """
    Test the creation of an FLT (Fast Lane Transfer) task using the detailed debugging FoodProductFactory.
    """
    # Ensure the category and product are created with all required attributes set correctly
    category = CategoryFactory.create()

    product = FoodProductFactory(
        category=category,
        quantity=100,  # Explicitly specify quantity to prevent IntegrityError
        unit_price=Decimal("16.99"),
        date_received=timezone.now().date() - datetime.timedelta(days=30),
        expiration_date=timezone.now().date() + datetime.timedelta(days=180)
    )

    # Create source and destination locations using the updated attributes
    source_location = LocationFactory.create(type='Inbound Floor', side='W', location_number=101)
    destination_location = LocationFactory.create(type='PND', side='E', location_number=102)

    # Create an FLT (Fast Lane Transfer) task
    flt_task = FLTTaskFactory.create(
        product=product,
        quantity=100,  # Ensure quantity is explicitly set if required by FLTTask model
        source_location=source_location,
        destination_location=destination_location,
        status='Pending'  # Assuming 'status' is a required field
    )

    # Assertions to verify the setup
    assert flt_task.product == product, "FLT task not associated with correct product."
    assert flt_task.quantity == 100, "FLT task quantity should be correctly set and retrieved."
    assert flt_task.source_location == source_location, "FLT task source location incorrect."
    assert flt_task.destination_location == destination_location, "FLT task destination location incorrect."
    assert flt_task.status == 'Pending', "FLT task not in 'Pending' status after creation."
    assert flt_task.assigned_to is None, "FLT task should not be assigned to anyone."

    # Additional checks to confirm the debug post-generation hooks are working
    assert product.quantity == 100, "Product quantity mismatch in post-generation."

    
@pytest.mark.django_db
def test_flt_task_creation():
    # Ensuring that all required fields are explicitly set
    category = CategoryFactory.create()
    product = FoodProductFactory(
        category=category,
        quantity=100,  # Explicitly setting quantity to avoid IntegrityError
        unit_price=Decimal("29.99"),
        date_received=timezone.now().date(),
        expiration_date=timezone.now().date() + datetime.timedelta(days=365)
    )

    # Create source and destination locations with specific settings
    source_location = LocationFactory(type='Storage', side='E', location_number=102)
    destination_location = LocationFactory(type='PND', side='W', location_number=103)

    # Create VNATask and ReplenishmentTask with explicit quantities
    vna_task = VNATaskFactory.create(
        task_type='Replenishment Picking',
        product=product,
        quantity=50,  # Explicitly setting quantity
        source_location=source_location,
        destination_location=destination_location,
        status='Assigned'
    )

    replenishment_task = ReplenishmentTaskFactory.create(
        product=product,
        source_location=source_location,
        destination_location=destination_location,
        quantity=50,  # Explicitly setting quantity
        status='Assigned'
    )

    # Create FLTTask with specific details and associations
    flt_task = FLTTaskFactory.create(
        product=product,
        source_location=destination_location,
        destination_location=LocationFactory(type='Pick Face', side='E', location_number=104),
        vna_task=vna_task,  # Assigning VNATask
        replenishment_task=replenishment_task,  # Assigning ReplenishmentTask
        status='Pending'
    )

    # Assertions to confirm proper linkage and status
    assert flt_task.vna_task == vna_task, "FLT task's VNA task does not match the expected VNA task."
    assert flt_task.replenishment_task == replenishment_task, "FLT task's replenishment task does not match the expected replenishment task."
    assert flt_task.status == 'Pending', "FLT task status should be 'Pending'."
    assert flt_task.product.quantity == 100, "Product quantity should be correctly set and retrieved."
    
    
@pytest.mark.django_db
def test_outbound_creation():
    outbound = OutboundFactory.create(
        code="OUT001",
        floor_number=1,
        bay_number=5,
        additional_info="Handle with care, fragile items area",
        max_capacity=500,
        operational_restrictions="No hazardous materials"
    )
    
    assert outbound.code == "OUT001"
    assert outbound.floor_number == 1
    assert outbound.bay_number == 5
    assert Outbound.objects.filter(code=outbound.code).exists()  
    
@pytest.mark.django_db
def test_pnd_location_handling():
    # Create a PND location with a specific temperature range
    pnd_location = PNDLocationFactory(temperature_range="5-10°C")
    
    assert pnd_location.capacity > 0, "Capacity should be properly set"
    assert pnd_location.temperature_range == "5-10°C", "Temperature range should match the specified value"




@pytest.fixture(autouse=True)
@pytest.mark.django_db
def setup_default_levels():
    # Setup default levels if they don't exist
    if not Level.objects.exists():
        Level.objects.create(id=1, name="Level 1")
logger = logging.getLogger(__name__)
 
@pytest.fixture(autouse=True, scope='module')
@pytest.mark.django_db
def setup_default_locations(db):
    if not Outbound.objects.exists():
        if not Level.objects.exists():
            rack = RackFactory.create()  # Create a rack if necessary
            Level.objects.create(
                rack=rack,
                level='G'  # Ground floor, assuming 'G' is a valid choice
            )
        default_level = Level.objects.first()

        if not default_level:
            logger.error("No Level found in the database; please ensure that Level objects are properly set up.")
            return

        try:
            Outbound.objects.create(
                name="Default Outbound",
                address="123 Example St",
                code="OUT001",
                description="Default description for outbound location.",
                level=default_level,
                side='E',
                location_number=1,
                weight=100.00,
                type='Outbound Floor',
                status='full',
                floor_number=1,
                bay_number=1,
                additional_info="No additional info",
                location_identifier="OUTBOUND_001",
                max_capacity=5000,
                operational_restrictions="None",
                special_handling_required=False
            )
            logger.info("Default Outbound location created successfully.")
        except (ValidationError, IntegrityError) as e:
            logger.error(f"Error setting up default Outbound location: {e}")







    
