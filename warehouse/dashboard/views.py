from django.shortcuts import render
from django.apps import apps



def dashboard_view(request):
    try:
        app_models = get_all_app_models()
        context = {
            'app_models': app_models,
        }
        return render(request, 'dashboard/index.html', context)
    except Exception as e:
        # Log the error here if you have logging set up
        context = {'error': str(e)}
        return render(request, 'dashboard/error.html', context)  # Assume you have an error.html template

def get_all_app_models():
    app_configs = apps.get_app_configs()
    app_models = {}

    for app_config in app_configs:
        app_models[app_config.name] = [model.__name__ for model in app_config.get_models()]
    
    return app_models



