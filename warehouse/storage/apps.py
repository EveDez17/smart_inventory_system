from django.apps import AppConfig
from django.db.models.signals import post_save


class StorageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "warehouse.storage"
    
    def ready(self):
        from warehouse.outbound.signals import handle_low_stock_pick_face 
