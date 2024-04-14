import pytest
from django.utils.timezone import make_aware
from datetime import datetime
from warehouse.inventory.models import FLTTask, VNATask, Zone, Aisle, Rack, Level, Location, PickFace
from warehouse.inventory.tests.test_db_fixtures import pnd_location
from warehouse.tests.factories import FoodProductFactory, CategoryFactory, LevelFactory

@pytest.fixture
@pytest.mark.django_db
def setup_environment(db):
    # Create structural components for the warehouse
    zone = Zone.objects.create(name="Default Zone", description="Storage Zone")
    aisle = Aisle.objects.create(zone=zone, aisle_letter='A')
    rack = Rack.objects.create(aisle=aisle, rack_number='1')
    level = Level.objects.create(rack=rack, level='G')  # 'G' for Ground level

    # Category and Product setup
    category = CategoryFactory(name="Ambient Food", slug='ambient-food')
    product = FoodProductFactory(
        sku="SKU00001",
        name="Beans",
        description="Premium beans",
        quantity=100,
        unit_price=1.50,
        expiration_date=make_aware(datetime.strptime("2023-12-31", "%Y-%m-%d")),
        category=category,
        date_received=make_aware(datetime.now())
    )

    # Create locations
    storage_location = Location.objects.create(
        code="STORAGE_001",
        name="Main Storage",
        level=level,
        side='E',
        location_number=1,
        type='Storage',
        status='full'
    )
    pnd_location = Location.objects.create(
        code="PND_002",
        name="PND Area",
        level=level,
        side='W',
        location_number=2,
        type='PND',
        status='empty'
    )
    pick_face_location = PickFace.objects.create(
        code="PICKFACE_003",
        name="Pick Face",
        level=level,
        side='E',
        location_number=3,
        type='Pick Face',
        status='low_stock',
        pick_face_code="PF_003",
        product=product,
        category=category,
        current_stock=5,
        low_stock_threshold=3,
        target_stock_level=50
    )

    return storage_location, pnd_location, pick_face_location, product, category

@pytest.mark.django_db
def test_replenishment_flow(setup_environment):
    storage, pnd, pick_face, product, category = setup_environment

    # Simulate a low stock scenario by manually updating the stock
    pick_face.current_stock = 2
    pick_face.save()

    # Create a VNATask for transferring stock from storage to PND
    vna_task = VNATask.objects.create(
        task_type='Replenishment Picking',
        product=product,
        quantity=20,  # Example quantity to transfer
        source_location=storage,
        destination_location=pnd,
        status='Assigned'
    )

    # Create an FLTTask linked to VNATask for transferring stock from PND to Pick Face
    flt_task = FLTTask.objects.create(
        task_type='Replenish Pick Face',
        product=product,
        quantity=pick_face.calculate_replenishment_quantity(),
        source_location=pnd,
        destination_location=pick_face,
        vna_task=vna_task,
        status='Assigned'
    )

    assert flt_task.vna_task == vna_task, "VNATask linking failed"
    assert flt_task.status == 'Assigned', "FLTTask status not set correctly"
    print("Test setup complete and assertions passed.")