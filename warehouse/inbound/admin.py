from django.contrib import admin
from .models import GatehouseBooking, ProvisionalBayAssignment, FinalBayAssignment, Inbound, Receiving, PutawayTask
from simple_history.admin import SimpleHistoryAdmin  # If you want to integrate django-simple-history

class GatehouseBookingAdmin(SimpleHistoryAdmin):
    list_display = ('driver_name', 'company', 'vehicle_registration', 'trailer_number', 'arrival_time')
    search_fields = ('driver_name', 'company', 'vehicle_registration', 'trailer_number')
    list_filter = ('arrival_time', 'company')

class ProvisionalBayAssignmentAdmin(SimpleHistoryAdmin):
    list_display = ('provisional_bay', 'assigned_by', 'assigned_at', 'gatehouse_booking')
    search_fields = ('provisional_bay', 'gatehouse_booking__driver_name')
    list_filter = ('assigned_at',)

class FinalBayAssignmentAdmin(SimpleHistoryAdmin):
    list_display = ('final_bay', 'confirmed_by', 'confirmed_at', 'is_loaded')
    search_fields = ('final_bay', 'provisional_bay_assignment__provisional_bay')
    list_filter = ('confirmed_at', 'is_loaded')

class InboundAdmin(SimpleHistoryAdmin):
    list_display = ('product', 'quantity', 'receiving_date', 'received_by', 'status', 'final_bay_assignment')
    search_fields = ('product__name', 'final_bay_assignment__final_bay')
    list_filter = ('status', 'receiving_date')

class ReceivingAdmin(SimpleHistoryAdmin):
    list_display = ('product', 'quantity', 'receiving_date', 'supplier', 'received_by')
    search_fields = ('product__name', 'supplier__name')
    list_filter = ('receiving_date', 'supplier')

class PutawayTaskAdmin(SimpleHistoryAdmin):
    list_display = ('inbound', 'assigned_to', 'start_time', 'status', 'pnd_location', 'pick_face')
    search_fields = ('inbound__product__name', 'pnd_location__description')
    list_filter = ('status', 'start_time')

# Register your models here
admin.site.register(GatehouseBooking, GatehouseBookingAdmin)
admin.site.register(ProvisionalBayAssignment, ProvisionalBayAssignmentAdmin)
admin.site.register(FinalBayAssignment, FinalBayAssignmentAdmin)
admin.site.register(Inbound, InboundAdmin)
admin.site.register(Receiving, ReceivingAdmin)
admin.site.register(PutawayTask, PutawayTaskAdmin)
