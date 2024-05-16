from django.urls import path
from . import views

urlpatterns = [
    path('outbound_dashboard/', views.outbound_dashboard, name='outbound_dashboard'),
]