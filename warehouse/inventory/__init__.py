# warehouse/inventory/__init__.py

# Import signals to ensure they are registered when the app is ready.
# This line will make Django discover and connect the signals as part of the app initialization.
default_app_config = 'warehouse.inventory.apps.InventoryConfig'
