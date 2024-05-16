from django.urls import path
from .views import dashboard_view, profile_view, reports_view, settings_view, logout_view

app_name = 'dashboard_global'

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('reports/', reports_view, name='reports'),
    path('settings/', settings_view, name='settings'),
    path('logout/', logout_view, name='logout'),
    
    
]