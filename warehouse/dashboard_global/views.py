from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
# warehouse/dashboard_global/views.py

from warehouse.inbound.views import InboundDashboardView



@login_required  # Optional: Ensures only logged-in users can access the dashboard
def dashboard_view(request):
    # You can add logic here to gather data to display on the dashboard
    context = {
        'user': request.user,
        'dashboard_data': {
            'number_of_visits': 34,  # Example data
            'favorite_section': 'Analytics'
        }
    }
    return render(request, 'dashboard.html', context)


def InboundDashboardView(request):
    InboundDashboardView(request)
    return render(request, 'inbound_dashboard.html')


@login_required
def profile_view(request):
    # Assuming you pass some context like user details
    return render(request, 'dashboard_global/profile.html')


def reports_view(request):
    # Your view logic here
    return render(request, 'reports.html')

@login_required
def settings_view(request):
    return render(request, 'dashboard_global/settings.html')

def logout_view(request):
    logout(request)  # This logs out the user
    return render(request, 'logout.html') 