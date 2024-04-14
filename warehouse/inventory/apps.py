from django.apps import AppConfig
from django.db.models.signals import post_save


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "warehouse.inventory"
    
    def ready(self):
        from .signals import handle_low_stock
        
        # Import the model on which the signal operates
        from .models import StockLevel
        
        # Connect the signal to the StockLevel model
        post_save.connect(handle_low_stock, sender=StockLevel, dispatch_uid="stock_level_low_stock_handler")