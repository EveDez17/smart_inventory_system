from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CombinedDataView,
    GatehouseBookingListView,
    GatehouseLogView,
    InboundDashboardView
)

app_name = 'inbound'

router = DefaultRouter()
router.register(r'gatehouse-bookings', GatehouseBookingListView)


urlpatterns = [
    
    path('dashboard/', InboundDashboardView.as_view(), name='inbound_dashboard'),
    path('gatehouse-log/', GatehouseLogView.as_view(), name='gatehouse_log'),
    path('api/combined-data/', CombinedDataView.as_view(), name='combined-data'),
    path('gatehouse-bookings/', GatehouseBookingListView.as_view(), name='gatehouse-bookings-list'),
    
]


