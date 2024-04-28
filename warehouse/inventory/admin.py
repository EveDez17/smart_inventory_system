
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Address, AuditLog, Category, FoodProduct, PredictionModel, Report, StockLevel, Supplier
from .models import Transaction

class CategoryAdmin(MPTTModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']
    list_filter = ['is_active']
    mptt_level_indent = 20
    
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street_number', 'street_name', 'city', 'county', 'country', 'post_code', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'email', 'contact_number', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')

class FoodProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'batch_number', 'expiration_date', 'is_expired']
    list_filter = ['is_high_demand', 'expiration_date']
    search_fields = ['sku', 'name', 'batch_number', 'description']
    date_hierarchy = 'expiration_date'

    def is_expired(self, obj):
        """Check if the product is expired based on the current date."""
        return obj.is_expired()
    is_expired.boolean = True  
    
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'action', 'user', 'timestamp')
    search_fields = ['content_type__model', 'object_id', 'user__username']
    list_filter = ('action', 'timestamp', 'user')
    readonly_fields = ('timestamp',)
    
class StockLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'location', 'quantity', 'batch_number', 'expiration_date', 'last_updated')
    list_filter = ('location', 'product', 'expiration_date')
    search_fields = ('product__name', 'location__name', 'batch_number')
    
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'status', 'amount', 'created_at', 'updated_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('description', 'amount')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('transaction_type', 'status', 'amount', 'description')
        }),
        ('Related Entities', {
            'fields': ('order', 'customer', 'supplier'),
            'classes': ('collapse',),
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'created_at', 'updated_at')
    search_fields = ('name', 'report_type')
    list_filter = ('report_type', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        return False  # Prevents adding new reports via the admin interface

    def has_delete_permission(self, request, obj=None):
        return False 
    
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_file')
    search_fields = ('name',)  # Allows searching by the 'name' field
    list_filter = ('name',) 
     
admin.site.register(PredictionModel)   
admin.site.register(StockLevel)   
admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(FoodProduct, FoodProductAdmin)


