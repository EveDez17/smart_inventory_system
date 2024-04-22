from django.urls import path
from . import views

urlpatterns = [
    path('storage/', views.storage_dashboard, name='storage_dashboard'),
]