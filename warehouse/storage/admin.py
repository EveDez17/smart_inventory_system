from django.contrib import admin
from .models import Zone, Aisle, Rack, Level, Location, PNDLocation, PickFace, Sensor, SensorData
from simple_history.admin import SimpleHistoryAdmin  # If you're using django-simple-history

# Register your models here.
@admin.register(Zone)
class ZoneAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'description', 'category')
    search_fields = ('name',)

@admin.register(Aisle)
class AisleAdmin(SimpleHistoryAdmin):
    list_display = ('zone', 'aisle_letter')
    list_filter = ('zone',)
    search_fields = ('aisle_letter',)

@admin.register(Rack)
class RackAdmin(SimpleHistoryAdmin):
    list_display = ('aisle', 'rack_number')
    list_filter = ('aisle',)

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('rack', 'level')
    list_filter = ('rack',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'level', 'side', 'location_number', 'weight', 'type', 'status')
    list_filter = ('level', 'type', 'status')
    search_fields = ('code', 'description')

@admin.register(PNDLocation)
class PNDLocationAdmin(admin.ModelAdmin):
    list_display = ('code', 'temperature_range', 'capacity', 'restrictions')
    search_fields = ('code',)

@admin.register(PickFace)
class PickFaceAdmin(admin.ModelAdmin):
    list_display = ('pick_face_code', 'parent_location', 'product', 'category', 'current_stock', 'low_stock_threshold', 'target_stock_level')
    list_filter = ('category',)
    search_fields = ('pick_face_code',)

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('location', 'sensor_type', 'status', 'last_checked')
    list_filter = ('sensor_type', 'status')
    search_fields = ('location__code',)

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'timestamp', 'data')
    list_filter = ('sensor', 'timestamp')
    search_fields = ('sensor__sensor_type',)

