from django.urls import path
from . import views

urlpatterns = [
    path('inventory_dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
]