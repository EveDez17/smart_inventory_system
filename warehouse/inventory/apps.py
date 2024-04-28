from django.apps import AppConfig
from django.conf import settings
import os
import joblib

from warehouse.dashboard_global import apps

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouse.inventory'

#    def ready(self):
#        # Ensure this code runs only once Django is fully ready and this app is installed
#        if not self.model:
#            model_path = os.path.join(settings.MEDIA_ROOT, 'demand_forecast_model.joblib')
#            try:
#                self.model = joblib.load(model_path)
#            except FileNotFoundError:
#                self.model = None  # Handle the absence of the model gracefully
#                # You might want to log this event
#                import logging
#                logger = logging.getLogger(__name__)
#                logger.warning(f"The model file at {model_path} was not found.")
#            except Exception as e:
#                # Handle other potential exceptions
#                raise ImportError(f"Could not load the model from {model_path}. Error: {e}") from e

#def get_forecast_model():
#    """
#    Function to get the loaded model from the app config.
#    This allows other parts of the application to access the model via this helper function.
#   """
#    return apps.get_app_config('inventory').model

