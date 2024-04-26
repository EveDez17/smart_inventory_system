from rest_framework import serializers
from warehouse.inbound.models import FinalBayAssignment, GatehouseBooking, ProvisionalBayAssignment

class GatehouseBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatehouseBooking
        fields = ['driver_name', 'company', 'vehicle_registration', 'trailer_number', 'arrival_time', 'has_paperwork', 'paperwork_description', 'cancelled']

class ProvisionalBayAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvisionalBayAssignment
        fields = ['gatehouse_booking', 'provisional_bay', 'assigned_by', 'assigned_at']

class FinalBayAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalBayAssignment
        fields = ['provisional_bay_assignment', 'final_bay', 'confirmed_by', 'confirmed_at', 'is_loaded', 'loaded_at', 'loader']
        
        
class CombinedSerializer(serializers.Serializer):
    gatehouse_bookings = serializers.SerializerMethodField()
    provisional_bay_assignments = serializers.SerializerMethodField()
    final_bay_assignments = serializers.SerializerMethodField()

    def get_gatehouse_bookings(self, obj):
        gatehouse_bookings = GatehouseBooking.objects.all()
        serializer = GatehouseBookingSerializer(gatehouse_bookings, many=True)
        return serializer.data

    def get_provisional_bay_assignments(self, obj):
        provisional_bay_assignments = ProvisionalBayAssignment.objects.all()
        serializer = ProvisionalBayAssignmentSerializer(provisional_bay_assignments, many=True)
        return serializer.data

    def get_final_bay_assignments(self, obj):
        final_bay_assignments = FinalBayAssignment.objects.all()
        serializer = FinalBayAssignmentSerializer(final_bay_assignments, many=True)
        return serializer.data
        
