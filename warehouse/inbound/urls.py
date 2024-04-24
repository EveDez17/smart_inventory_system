from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inbound'

router = DefaultRouter()
router.register(r'gatehouse-bookings', views.GatehouseBookingViewSet)
router.register(r'provisional-bay-assigment', views.ProvisionalBayAssignmentViewSet)
router.register(r'final-bay-assigment', views.FinalBayAssignmentViewSet)

urlpatterns = [
    path('inbound_dashboard/', views.inbound_dashboard, name='inbound_dashboard'),
    path('gatehouse_booking/', views.book_gatehouse, name='gatehouse_booking'),
    path('gatehouse-bookings/', views.gatehouse_bookings_list, name='gatehouse-bookings-list'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking-list-fragment/', views.booking_list_fragment, name='booking_list_fragment'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('provisional-bays/', views.provisional_bay_list, name='provisional-bay-list'),
    
    path('api/', include(router.urls)),
]