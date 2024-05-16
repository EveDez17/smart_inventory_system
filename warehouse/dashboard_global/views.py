from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
# warehouse/dashboard_global/views.py

from warehouse.inbound.models import FLTTask, FinalBayAssignment, GatehouseBooking, Inbound
from warehouse.inbound.views import InboundDashboardView
from warehouse.inventory.models import FoodProduct
from django.db.models import Sum

from warehouse.outbound.models import Outbound



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
    return render(request, 'users_dashboard.html')

def logout_view(request):
    logout(request)  # This logs out the user
    return render(request, 'logout.html') 



def dashboard_view(request):
    # Data for display
    total_food_products = FoodProduct.objects.count()
    to_be_delivered = FinalBayAssignment.objects.filter(is_loaded=True).count()
    recent_gatehouse_bookings = GatehouseBooking.objects.order_by('-arrival_time')[:5]
    low_stock_products = FoodProduct.objects.filter(stock__lte=5)

    # Data for charts
    product_stock_values = list(
        FoodProduct.objects.values('name')
        .annotate(total_stock=Sum('stock'))
        .order_by('-total_stock')[:5]
    )
    product_labels = [product['name'] for product in product_stock_values]
    stock_data = [product['total_stock'] for product in product_stock_values]

    # Inbound and FLT Tasks Data
    recent_inbound_tasks = Inbound.objects.select_related('product', 'final_bay_assignment').order_by('-receiving_date')[:5]
    recent_flt_tasks = FLTTask.objects.select_related('product', 'source_location', 'destination_location').order_by('-start_time')[:5]

    # Outbound Tasks Data
    # This should correspond to some logic defining recent outbound tasks.
    # As there is no Outbound model in the provided code, this is commented out for now.
    # If you have an Outbound model with a 'status' field or similar, uncomment and adjust the following line:
    # recent_outbound_tasks = Outbound.objects.filter(status='In Progress').order_by('-some_date_field')[:5]
    
    # Placeholder data for To-Do List
    todo_list = [
        {'task': 'Check inventory levels', 'due_date': '2024-05-05'},
        {'task': 'Schedule maintenance', 'due_date': '2024-05-10'},
        {'task': 'Update product listings', 'due_date': '2024-05-15'},
    ]

    # Placeholder data for Chat Notifications
    chat_notifications = [
        {'message': 'New message from Supplier ABC', 'timestamp': '10:30 AM'},
        {'message': 'Warehouse team chat updated', 'timestamp': 'Yesterday'},
    ]

    context = {
        'total_food_products': total_food_products,
        'to_be_delivered': to_be_delivered,
        'recent_gatehouse_bookings': recent_gatehouse_bookings,
        'low_stock_products': low_stock_products,
        'product_labels': product_labels,
        'stock_data': stock_data,
        'recent_inbound_tasks': recent_inbound_tasks,
        'recent_flt_tasks': recent_flt_tasks,
        'todo_list': todo_list,
        'chat_notifications': chat_notifications,
        # 'recent_outbound_tasks': recent_outbound_tasks,  # Uncomment once you define the Outbound model logic
    }

    return render(request, 'dashboard.html', context)
