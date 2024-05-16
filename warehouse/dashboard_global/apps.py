from django.apps import AppConfig


class DashboardGlobalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "warehouse.dashboard_global"
    
    def ready(self):
        import warehouse.dashboard_global.signals
  