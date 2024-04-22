from django.urls import path
from . import views

app_name = 'inbound'

urlpatterns = [
    path('inbound/', views.inbound_dashboard, name='inbound'),
    path('gatehouse_booking/', views.book_gatehouse, name='gatehouse_booking'),
    path('gatehouse-bookings/', views.gatehouse_bookings_list, name='gatehouse-bookings-list'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking-list-fragment/', views.booking_list_fragment, name='booking_list_fragment'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('provisional-bays/', views.provisional_bay_list, name='provisional-bay-list'),
]