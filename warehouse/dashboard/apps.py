from django.apps import AppConfig
from django.shortcuts import render
from django.apps import apps


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "warehouse.dashboard"
def dashboard_view(request):
    app_names = ['users', 'inbound', 'outbound', 'storage', 'inventory']
    app_models = {}

    for app_name in app_names:
        app_models[app_name] = get_models_for_app(app_name)
    
    context = {
        'app_models': app_models,
    }
    return render(request, 'dashboard/index.html', context)

def get_models_for_app(app_name):
    models = apps.get_app_config(app_name).get_models()
    return models