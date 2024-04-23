from rest_framework import serializers
from .models import FinalBayAssignment, GatehouseBooking, ProvisionalBayAssignment

class GatehouseBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatehouseBooking
        fields = '__all__' 
        
class ProvisionalBayAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvisionalBayAssignment
        fields = fields = '__all__' 
        
class FinalBayAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalBayAssignment
        fields = fields = '__all__' 
        
