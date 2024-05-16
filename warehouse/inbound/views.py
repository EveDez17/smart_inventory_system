from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from warehouse.inbound.models import FinalBayAssignment, GatehouseBooking, Inbound, ProvisionalBayAssignment
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from .forms import FinalBayAssignmentForm, GatehouseBookingForm, ProvisionalBayAssignmentForm
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth import get_user_model

User = get_user_model()

class InboundDashboardView(APIView):
    def get(self, request):
        return render(request, 'inbound_dashboard.html')
    


def inbound_dashboard(request):
    recent_activities = GatehouseBooking.objects.order_by('-arrival_time')[:5]
    summary_data = {
        'total_bookings': GatehouseBooking.objects.count(),
        'total_inbounds': Inbound.objects.count(),
        # Add other summary items...
    }
    
    # Imagine you have some system notifications or messages to display
    system_messages = ['System will be down for maintenance at midnight.', 'New features have been added to the inventory section.']
    
    # And some generic announcements or alerts
    alerts = ['New parking policy will be effective from next Monday.', 'Remember to verify your contact details in your profile.']
    
    context = {
        'recent_activities': recent_activities,
        'summary_data': summary_data,
        'system_messages': system_messages,
        'alerts': alerts,
    }
    return render(request, 'inbound/inbound_dashboard.html', context)



class GatehouseLogView(APIView):
    def get(self, request):
        return render(request, 'inbound/gatehouse_log.html')
    
    


def register_booking(request):
    if request.method == 'POST':
        form = GatehouseBookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking successfully created!')
            return redirect('inbound:gatehouse_log')  
    else:
        form = GatehouseBookingForm()  

    return render(request, 'inbound/register_booking.html', {'form': form})


class ProvisionalBayAssignmentListView(ListView):
    model = ProvisionalBayAssignment
    template_name = 'inbound/provisional_bay_assignment_list.html'
    context_object_name = 'assignments'
    


class ProvisionalBayAssignmentCreateView(CreateView):
    model = ProvisionalBayAssignment
    form_class = ProvisionalBayAssignmentForm
    template_name = 'inbound/provisional_bay_assignment_form.html'
    success_url = reverse_lazy('inbound:gatehouse_log')  # Redirect after creation

    def form_valid(self, form):
        # Set the 'created_by' field to the user with pk=2
        form.instance.created_by = get_object_or_404(User, pk=2)
        # Now call the super method to save the object
        return super().form_valid(form)
    
# Is not working do to the approch revised requires
#class GatehouseLogView(View):
#    def get(self, request):
#        # Query the database to get booking data
#        bookings = GatehouseBooking.objects.all()
#
#       # Serialize the booking data into JSON format
#        booking_data = [{
#            'driver_name': booking.driver_name,
#            'company': booking.company,
#            'vehicle_registration': booking.vehicle_registration,
#            'trailer_number': booking.trailer_number,
#            'arrival_time': booking.arrival_time,
#            'has_paperwork': booking.has_paperwork,
#            'paperwork_description': booking.paperwork_description,
#            'cancelled': booking.cancelled,
#        } for booking in bookings]

#        # Return the JSON response
#        return JsonResponse({'bookings': booking_data})


class UserPkPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        # Allow only users with certain primary keys or superusers
        allowed_pks = [5, 6, 7, 8, 9, 10, 11]
        return self.request.user.pk in allowed_pks or self.request.user.is_superuser

    def handle_no_permission(self):
        # If the user does not have permission, return HTTP Forbidden
        return HttpResponseForbidden("You do not have permission to access this page.")

class FinalBayAssignmentListView(LoginRequiredMixin, UserPkPermissionMixin, ListView, FormMixin):
    model = FinalBayAssignment
    form_class = FinalBayAssignmentForm
    template_name = 'inbound/final_bay_assignment_list.html'
    context_object_name = 'final_bay_assignments'
    success_url = reverse_lazy('inbound:final_bay_assignment_list')  # Redirect URL after form is successfully submitted

    def get_context_data(self, **kwargs):
        # Include the form in the context for the template
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        # Handling the POST request for the form
        self.object = None  # This is needed because ListView does not support handling of forms
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # What to do if the form is valid
        form.save()
        return redirect(self.get_success_url())  # Redirecting to the success URL

    def form_invalid(self, form):
        # What to do if the form is not valid
        # Render the list view with the form errors
        return self.render_to_response(self.get_context_data(form=form))
    
class GatehouseLogView(ListView):
    template_name = 'inbound/gatehouse_log.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return ProvisionalBayAssignment.objects.all()
    
