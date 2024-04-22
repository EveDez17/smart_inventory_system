from django.urls import path
from . import views

app_name = 'inbound'

urlpatterns = [
    path('inbound/', views.inbound_dashboard, name='inbound'),
    path('gatehouse_booking/', views.book_gatehouse, name='gatehouse_booking'),
    path('gatehouse-bookings/', views.gatehouse_bookings_list, name='gatehouse-bookings-list'),
    path('provisional-bays/', views.provisional_bay_list, name='provisional-bay-list'),
]