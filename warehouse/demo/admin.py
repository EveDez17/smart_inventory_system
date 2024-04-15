from django.contrib import admin
from warehouse.inventory.models import CMR, Category, LoaderTask, Report, Transaction

admin.site.register(Category)



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


    


