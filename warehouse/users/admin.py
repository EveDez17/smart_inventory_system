from django.contrib import admin
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from warehouse.inventory.models import CMR, Category, LoaderTask, Report, Transaction
from .models import User, Employee

# Get the custom User model
User = get_user_model()

# Define the custom forms for User creation and modification
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

# Define the custom UserAdmin
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = User
    list_display = ('email', 'role', 'is_staff', 'is_active',)
    list_filter = ('role', 'is_staff', 'is_active',)
    fieldsets = (
        ('User Info', {'fields': ('email', 'password',)}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_active', 'is_staff',)
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

# Attempt to unregister the existing User admin if it has been registered previously.
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        count = queryset.update(is_approved=True)
        if count == 1:
            message_bit = "1 user was"
        else:
            message_bit = f"{count} users were"
        self.message_user(request, f"{message_bit} successfully approved.", messages.SUCCESS)
    approve_users.short_description = "Approve selected users"

admin.site.register(User, CustomUserAdmin)

# Register other models
admin.site.register(Employee)
admin.site.register(Category)
# ... register other models ...

# Customizing the admin site's header, title, and index title
admin.site.site_header = "Warehouse Inventory Management Admin"
admin.site.site_title = "Warehouse Inventory Site Admin"
admin.site.index_title = "Warehouse Inventory Overview"




@admin.register(LoaderTask)
class LoaderTaskAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'status', 'completion_time', 'confirmed_by')
    actions = ['confirm_completion']

    def confirm_completion(self, request, queryset):
        queryset.update(status='Completed', confirmed_by=request.user)
        for task in queryset:
            # Assuming auto-CMR creation is enabled
            self.create_cmr_if_ready(task.dispatch)
        self.message_user(request, "Selected tasks have been confirmed.")
    confirm_completion.short_description = "Confirm completion of selected tasks"

    def create_cmr_if_ready(self, dispatch):
        if dispatch.loader_tasks.filter(status__in=['Pending', 'In Progress']).exists():
            return  # Not all tasks are completed

        # Create CMR if all tasks are completed and not yet created
        if not hasattr(dispatch, 'cmr'):
            CMR.objects.create(
                dispatch=dispatch,
                confirmed_by=self.request.user,
                document="path/to/generated/document.pdf"  # Generate this document as needed
            )
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'created_at']
    actions = ['run_report']

    def run_report(self, request, queryset):
        for report in queryset:
            report_data = report.generate_report()
            # Here you could implement methods to download as CSV, log to console, or display in the admin
            self.message_user(request, f"Report generated successfully for {report.name}: {report_data}")

    run_report.short_description = "Generate selected reports"
    
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'amount', 'status', 'order', 'customer', 'supplier', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['order__id', 'customer__name', 'supplier__name', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


    


