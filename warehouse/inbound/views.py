from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from warehouse.inbound.models import FinalBayAssignment, GatehouseBooking, ProvisionalBayAssignment
from .serializers import FinalBayAssignmentSerializer, GatehouseBookingSerializer, ProvisionalBayAssignmentSerializer
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
import django_filters


class InboundDashboardView(APIView):
    def get(self, request):
        return render(request, 'inbound_dashboard.html')


class GatehouseLogView(APIView):
    def get(self, request):
        return render(request, 'inbound/gatehouse_log.html')

class CombinedDataView(APIView):
    """
    API endpoint that retrieves combined data related to gatehouse bookings,
    provisional bay assignments, and final bay assignments. This view is protected,
    meaning only authenticated users can access this data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Retrieve data from the database
        gatehouse_bookings = GatehouseBooking.objects.all()
        provisional_bay_assignments = ProvisionalBayAssignment.objects.all()
        final_bay_assignments = FinalBayAssignment.objects.all()

        # Serialize the data using DRF serializers
        data = {
            'gatehouse_bookings': GatehouseBookingSerializer(gatehouse_bookings, many=True).data,
            'provisional_bay_assignments': ProvisionalBayAssignmentSerializer(provisional_bay_assignments, many=True).data,
            'final_bay_assignments': FinalBayAssignmentSerializer(final_bay_assignments, many=True).data
        }
        
        # Return a HTTP 200 OK response with serialized data
        return Response(data, status=status.HTTP_200_OK)
    
class GatehouseBookingFilter(django_filters.FilterSet):
    min_arrival_time = django_filters.DateTimeFilter(field_name='arrival_time', lookup_expr='gte')
    max_arrival_time = django_filters.DateTimeFilter(field_name='arrival_time', lookup_expr='lte')
    driver_name_contains = django_filters.CharFilter(field_name='driver_name', lookup_expr='icontains')

    class Meta:
        model = GatehouseBooking
        fields = ['driver_name', 'min_arrival_time', 'max_arrival_time', 'driver_name_contains']

class GatehouseBookingListView(ListAPIView):
    queryset = GatehouseBooking.objects.all()
    serializer_class = GatehouseBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GatehouseBookingFilter
    search_fields = ['driver_name', 'company', 'vehicle_registration']  # Define searchable fields
    ordering_fields = ['arrival_time', 'driver_name']
    ordering = ['arrival_time']  # Default ordering
    pagination_class = PageNumberPagination 