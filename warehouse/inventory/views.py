from django.views.generic import ListView
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.generic import TemplateView
from rest_framework.views import APIView
from warehouse.inventory.pdf_utils import extract_data_from_pdf, process_data
from warehouse.inventory.utils import prepare_pie_chart_data
from .models import AuditLog, Category, FoodProduct, Report, StockLevel, Supplier, Transaction
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from .forms import AddressForm, CategoryForm, FoodProductForm, StockLevelForm, SupplierForm
from django.views import View
from django.db import transaction
from django.views.generic.edit import UpdateView



class InventoryDashboardView(TemplateView):
    template_name = 'inventory_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = FoodProduct.objects.all()  # Fetch all products
        # Add more context variables as needed, such as statistics or alerts
        return context
    
 # Category Products Views
    
def category_list(request):
    # Retrieve all active categories
    categories = Category.objects.filter(is_active=True)

    # Pass categories to the template for rendering
    return render(request, 'inventory/category_list.html', {'categories': categories}) 

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:category_list')  # Assuming 'category_list' is the URL name for the category list page
    else:
        form = CategoryForm()
    return render(request, 'inventory/add_category.html', {'form': form})

# Food Product Views
class FoodProductCreateView(CreateView):
    form_class = FoodProductForm
    template_name = 'inventory/food_product_create.html'  
    success_url = reverse_lazy('inventory:inventory_dashboard')  # URL to redirect after successful creation

    def form_valid(self, form):
        # You can add any logic you want to be triggered after form validation here
        return super().form_valid(form)
    
class ProductEditRedirectView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        if product_id:
            return redirect('inventory:food_product_edit', pk=product_id)
        else:
            # Handle the case where no product is selected
            return redirect('inventory_dashboard')
        
class FoodProductUpdateView(UpdateView):
    model = FoodProduct
    form_class = FoodProductForm
    template_name = 'inventory/food_product_edit.html'  # The template to display the form
    # This attribute defines the URL to redirect after the form is successfully submitted.
    # You can set this to a dynamic value if needed (like a detail view of the product).
    success_url = reverse_lazy('inventory:inventory_dashboard') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Edit'
        return context
    

class ProductDeleteRedirectView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(FoodProduct, pk=product_id)
        return redirect('inventory:food_product_confirm_delete', pk=product.pk)

    
class FoodProductConfirmDeleteView(DeleteView):
    model = FoodProduct
    template_name = 'inventory/food_product_confirm_delete.html'
    success_url = reverse_lazy('inventory:inventory_dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Delete'
        return context
    
def product_delete(request, pk):
    product = get_object_or_404(FoodProduct, pk=pk)
    product.delete()
    return JsonResponse({'success': True, 'redirect_url': reverse('inventory:inventory_dashboard')})

def search_results(request):
    search_query = request.GET.get('search_query', '')
    products = FoodProduct.objects.filter(sku__icontains=search_query)
    return render(request, 'inventory/search_results.html', {
        'products': products,
        'search_query': search_query
    })
    
def sku_details(request, pk):
    sku = get_object_or_404(FoodProduct, pk=pk)
    return render(request, 'inventory/product_detail.html', {'sku': sku})

# Supplier Dashboard

class SuppliersDashboardView(TemplateView):
    template_name = 'suppliers_dashboard.html'
    
class SupplierListView(ListView):
    model = Supplier
    template_name = 'suppliers/list.html'

class SupplierCreateUpdateView(CreateView, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/form.html'
    success_url = reverse_lazy('supplier-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('pk'):
            context['address_form'] = AddressForm(instance=self.object.address)
        else:
            context['address_form'] = AddressForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        address_form = context['address_form']
        with transaction.atomic():
            if address_form.is_valid():
                address = address_form.save()
                supplier = form.save(commit=False)
                supplier.address = address
                supplier.save()
                return redirect(self.get_success_url())
            else:
                return self.form_invalid(form)

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'suppliers/confirm_delete.html'
    success_url = reverse_lazy('supplier-list')
    

# Audit Log

def audit_log_list(request):
    # Retrieve all audit logs
    audit_logs = AuditLog.objects.all()

    # Render the template with audit logs
    return render(request, 'inventory/audit_log_list.html', {'audit_logs': audit_logs})

#Stock Level

class StockLevelDashboardView(TemplateView):
    template_name = 'stock/stock_level_dashboard.html'
    
class StockLevelListView(ListView):
    model = StockLevel
    template_name = 'stock/stock_level_list.html'
    context_object_name = 'stock_levels'

def create_stock_level(request):
    if request.method == 'POST':
        form = StockLevelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:stock_level_list')  # Redirect to the stock level list
    else:
        form = StockLevelForm()
    return render(request, 'stock/stock_level_create.html', {'form': form})

def update_stock(request, stock_id):
    if request.method == 'POST':
        new_level = request.POST.get('new_stock_level')
        stock = StockLevel.objects.get(pk=stock_id)
        stock.level = new_level
        stock.save()
        return redirect('inventory:stock_level_list') 

class StockLevelDeleteView(DeleteView):
    model = StockLevel
    template_name = 'stock/stock_level_confirm_delete.html'
    success_url = reverse_lazy('stock_level_list')
    
 
def stock_level_dashboard(request):
    stock_levels = StockLevel.objects.all()
    # Prepare data for rendering the pie chart
    chart_data = prepare_pie_chart_data(stock_levels)
    return render(request, 'stock/stock_level_dashboard.html', {'chart_data': chart_data})

def generate_pie_counts_from_pdf(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            # Handle the case where no file is uploaded
            return HttpResponseBadRequest("No PDF file uploaded.")

        try:
            extracted_text = extract_data_from_pdf(pdf_file)
            categories, counts = process_data(extracted_text)
            chart_data = prepare_pie_chart_data(categories, counts)
            return render(request, 'stock/stock_level_dashboard.html', {'chart_data': chart_data})
        except Exception as e:
            # Handle errors in processing, e.g., file format errors
            return HttpResponseBadRequest(f"Error processing file: {str(e)}")

    return render(request, 'stock/generate_pie_counts_from_pdf.html')

#Transaction View

def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-created_at')  # Getting all transactions ordered by creation date
    return render(request, 'transaction/transaction_list.html', {'transactions': transactions})

def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    return render(request, 'transaction/transaction_detail.html', {'transaction': transaction})

#Reports
def reports_view(request):
    # This view simply renders the reports main page.
    return render(request, 'inventory/reports.html')

def report_list_view(request):
    # This view gathers data about all reports and passes it to the template.
    reports = Report.objects.all()
    report_data = []
    for report in reports:
        report_data.append({
            'id': report.id,
            'name': report.name,
            'type': report.report_type,
            'data': report.generate_report(),
        })
    return render(request, 'inventory/report-list.html', {'report_data': report_data})

def report_detail_view(request, report_id):
    # This view fetches a single report by its ID and passes its details to the template.
    report = get_object_or_404(Report, id=report_id)
    report_data = report.generate_report()
    return render(request, 'inventory/report-detail.html', {'report': report, 'report_data': report_data})

