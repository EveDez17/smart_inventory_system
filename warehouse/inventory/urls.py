from django.urls import path
from . import views

app_name= 'inventory'

urlpatterns = [
   
    path('dashboard/', views.InventoryDashboardView.as_view(), name='inventory_dashboard'),
    # Categories URLS
    path('categories/', views.category_list, name='category_list'),
    path('add_category/', views.add_category, name='add_category'),
     # Product URLS
    path('products/new/', views.FoodProductCreateView.as_view(), name='food_product_create'),
    path('products/edit/redirect/', views.ProductEditRedirectView.as_view(), name='food_product_edit_redirect'),
    path('products/<int:pk>/edit/', views.FoodProductUpdateView.as_view(), name='food_product_edit'),
    path('products/delete/redirect/', views.ProductDeleteRedirectView.as_view(), name='food_product_delete_redirect'),
    path('products/<int:pk>/delete/', views.FoodProductConfirmDeleteView.as_view(), name='food_product_confirm_delete'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('search/', views.search_results, name='inventory_search_results'),
    path('product/<int:pk>/details/', views.sku_details, name='product_detail'),
    
    # Supplier URLS
    path('suppliers_dashboard/', views.SuppliersDashboardView.as_view(), name='suppliers_dashboard'),
    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/add/', views.SupplierCreateUpdateView.as_view(), name='supplier-add'),  # Create
    path('suppliers/<int:pk>/edit/', views.SupplierCreateUpdateView.as_view(), name='supplier-update'),  # Update
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier-delete'),  # Delete
    
    #Audit Log URL
     path('audit-logs/', views.audit_log_list, name='audit_log_list'),
     
    #Stock Level URLS
    path('stock/dashboard/', views.StockLevelDashboardView.as_view(), name='stock_level_dashboard'),
    path('stock/levels/', views.StockLevelListView.as_view(), name='stock_level_list'),
    path('stock_level_create/', views.create_stock_level, name='stock_level_create'),
    path('update-stock/<int:stock_id>/', views.update_stock, name='update-stock'),
    path('stock/levels/<int:pk>/delete/', views.StockLevelDeleteView.as_view(), name='stock_level_delete'),
    path('dashboard/', views.stock_level_dashboard, name='stock_dashboard'),
    path('generate_pie_counts/', views.generate_pie_counts_from_pdf, name='generate_pie_counts_from_pdf'),
    
    #Transaction URLS
    
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    
    #Reports
    path('reports/', views.reports_view, name='reports'),
    path('report-list/', views.report_list_view, name='report-list'),
    path('report-detail/<int:report_id>/', views.report_detail_view, name='report-detail'),
]