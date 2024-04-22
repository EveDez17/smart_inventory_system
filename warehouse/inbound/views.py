from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from warehouse.inbound.models import GatehouseBooking, ProvisionalBayAssignment
from .forms import GatehouseBookingForm, SearchForm

def inbound_dashboard(request):
    return render(request, 'inbound/dashboard.html')

# Gatehouse Register
def book_gatehouse(request):
    if request.method == 'POST':
        form = GatehouseBookingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('inbound:gatehouse-bookings-list'))  
    else:
        form = GatehouseBookingForm()
    return render(request, 'inbound/gatehouse_booking.html', {'form': form})

#Gatehouse bookings
def gatehouse_bookings_list(request):
    if request.method == 'POST':
        form = GatehouseBookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inbound/gatehouse-bookings-list')
    else:
        form = GatehouseBookingForm()

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

