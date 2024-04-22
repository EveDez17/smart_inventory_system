from django.shortcuts import render

def outbound_dashboard(request):
    # Your code here
    return render(request, 'storage/dashboard.html', {})