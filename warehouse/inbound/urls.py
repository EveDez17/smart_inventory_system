from django.urls import path

from .views import (
    FinalBayAssignmentListView,
    GatehouseLogView,
    InboundDashboardView,
    ProvisionalBayAssignmentCreateView,
    ProvisionalBayAssignmentListView,
    register_booking
)
from warehouse.inbound import views

app_name='Inbound'

urlpatterns = [
    
    path('dashboard/', InboundDashboardView.as_view(), name='inbound_dashboard'),
    path('gatehouse-log/', GatehouseLogView.as_view(), name='gatehouse_log'),
    path('register-booking/', register_booking, name='register_booking'),
    path('provisional-bay-assignments/', ProvisionalBayAssignmentListView.as_view(), name='provisional_bay_assignments'),
    path('create-provisional-bay-assignment/', ProvisionalBayAssignmentCreateView.as_view(), name='create_provisional_bay_assignment'),
    path('final-bay-assignments/', FinalBayAssignmentListView.as_view(), name='final_bay_assignments'),
   
    
    
]


