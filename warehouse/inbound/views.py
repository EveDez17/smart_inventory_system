from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from warehouse.inbound.models import GatehouseBooking, ProvisionalBayAssignment
from simple_history.utils import update_change_reason
from .forms import GatehouseBookingForm, SearchForm
from rest_framework import viewsets
from .models import FinalBayAssignment, GatehouseBooking
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import FinalBayAssignmentSerializer, GatehouseBookingSerializer, ProvisionalBayAssignmentSerializer

class GatehouseBookingViewSet(viewsets.ModelViewSet):
    queryset = GatehouseBooking.objects.all()
    serializer_class = GatehouseBookingSerializer
    permission_classes = [IsAuthenticated]
    
    # Optionally add search functionality
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search')
        if search_term:
            queryset = queryset.filter(driver_name__icontains=search_term)
        return queryset
    
class ProvisionalBayAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ProvisionalBayAssignment.objects.all()
    serializer_class = ProvisionalBayAssignmentSerializer
    
    # Optionally add search functionality
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search')
        if search_term:
            queryset = queryset.filter(driver_name__icontains=search_term)
        return queryset
    
class FinalBayAssignmentViewSet(viewsets.ModelViewSet):
    queryset = FinalBayAssignment.objects.all()
    serializer_class = FinalBayAssignmentSerializer
    
    # Optionally add search functionality
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search')
        if search_term:
            queryset = queryset.filter(driver_name__icontains=search_term)
        return queryset










def inbound_dashboard(request):
    return render(request, 'inbound/dashboard.html')

 #Gatehouse Register
def book_gatehouse(request):
    if request.method == 'POST':
        form = GatehouseBookingForm(request.POST, request.FILES)
        if form.is_valid():
           form.save()
            # Add a success message to be displayed after the redirect
           messages.success(request, 'Gatehouse entry registered successfully.')
           # Redirect to the gatehouse bookings list
        return redirect(reverse('inbound:gatehouse-bookings-list'))
    else:
        form = GatehouseBookingForm()

    return render(request, 'inbound/gatehouse_booking.html', {'form': form})

#Gatehouse bookings
def gatehouse_bookings_list(request):
    form = GatehouseBookingForm()
    search_form = SearchForm()

    if request.method == 'POST':
        if 'delete' in request.POST:
            booking_id = request.POST.get('delete')
            booking = get_object_or_404(GatehouseBooking, id=booking_id)
            booking.delete()
            update_change_reason(booking, 'Deleted by user.')
            messages.success(request, 'The booking has been deleted successfully.')
            return redirect('inbound:gatehouse-bookings-list')
        
        elif 'cancel' in request.POST:
            booking_id = request.POST.get('cancel')
            booking = get_object_or_404(GatehouseBooking, id=booking_id)
            booking.status = 'cancelled'  # Update with your status field
            update_change_reason(booking, 'Cancelled by user.')
            booking.save()
            messages.success(request, 'The booking has been cancelled successfully.')
            return redirect('inbound:gatehouse-bookings-list')
        
        else:
            form = GatehouseBookingForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Booking added successfully.')
                return redirect('inbound:gatehouse-bookings-list')

    bookings = GatehouseBooking.objects.all()  # or any other logic you have for fetching bookings
    return render(request, 'inbound/gatehouse_bookings_list.html', {
        'bookings': bookings,
        'search_form': search_form,
        'form': form
    })

    # Handle the search functionality
    search_form = SearchForm(request.GET)
    if search_form.is_valid() and search_form.cleaned_data['search_term']:
        search_term = search_form.cleaned_data['search_term']
        bookings = GatehouseBooking.objects.filter(
            driver_name__icontains=search_term
        )
    else:
        bookings = GatehouseBooking.objects.all()

    return render(request, 'inbound/gatehouse_bookings_list.html', {
        'bookings': bookings,
        'search_form': search_form,
        'form': form
    })


#Waiting Bay

def provisional_bay_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        assignments = ProvisionalBayAssignment.objects.filter(
            Q(provisional_bay__icontains=search_query) | 
            Q(gatehouse_booking__driver_name__icontains=search_query)
        )
    else:
        assignments = ProvisionalBayAssignment.objects.all()

    return render(request, 'inbound/provisional_bay_list.html', {
        'assignments': assignments
    })
 # Waiting List Search   
def provisional_bay_list(request):
    search_query = request.GET.get('search', '')
    date_query = request.GET.get('date', '')
    
    assignments = ProvisionalBayAssignment.objects.all()
    
    if search_query:
        assignments = assignments.filter(
            Q(provisional_bay__icontains=search_query) | 
            Q(gatehouse_booking__driver_name__icontains=search_query)
        )
    
    if date_query:
        assigned_date = timezone.datetime.strptime(date_query, '%Y-%m-%d').date()
        assignments = assignments.filter(assigned_at__date=assigned_date)
    
    return render(request, 'inbound/provisional_bay_list.html', {
        'assignments': assignments
    })
    
# Cancel Booking View
    
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(GatehouseBooking, pk=booking_id)
    booking.cancelled = True
    booking.save()
    return JsonResponse({'cancelled': True, 'booking_id': booking_id})

#Update List after Cancellation

def booking_list_fragment(request):
    bookings = GatehouseBooking.objects.all()  # Or any filtering based on session or criteria
    return render(request, 'inbound/booking_list_fragment.html', {'bookings': bookings})



# Booking History View
def booking_history_view(request, booking_id):
    booking = get_object_or_404(GatehouseBooking, pk=booking_id)
    history = booking.history.all()
    return render(request, 'booking_history.html', {'history': history})
 
# Delete Booking View

def delete_booking(request, booking_id):
    booking = get_object_or_404(GatehouseBooking, pk=booking_id)
    booking.delete()
    messages.success(request, "Booking deleted successfully.")
    return redirect(reverse('inbound:gatehouse-bookings-list'))


