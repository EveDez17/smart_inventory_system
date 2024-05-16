from django.urls import path
from .views import StorageDashboardView
from . import views

app_name = 'storage'  

urlpatterns = [
   path('dashboard/', StorageDashboardView.as_view(), name='storage_dashboard'),
   
]
