from django.shortcuts import render

def inventory_dashboard(request):
    # Your code here
    return render(request, 'inventory_dashboard/dashboard.html', {})
