from django.shortcuts import render

def storage_dashboard(request):
    # Your code here
    return render(request, 'storage_dashboard/dashboard.html', {})