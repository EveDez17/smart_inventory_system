from django.urls import path
from . import views

app_name = 'inbound'

urlpatterns = [
    path('inbound/', views.inbound_dashboard, name='inbound'),
    # Ensure there's at least one valid URL pattern here
]