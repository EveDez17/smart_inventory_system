from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import GatehouseBookingForm

def inbound_dashboard(request):
    return render(request, 'inbound/dashboard.html')

def book_gatehouse(request):
    if request.method == 'POST':
        form = GatehouseBookingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('gatehouse_bookings_list'))  # Redirect to a view that shows all bookings
    else:
        form = GatehouseBookingForm()
    return render(request, 'your_app/gatehouse_booking_form.html', {'form': form})

