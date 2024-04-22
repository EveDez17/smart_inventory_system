from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.outbound_dashboard, name='outbound_dashboard'),
]