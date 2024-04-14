from django.contrib import admin

from warehouse.inventory.models import CMR, LoaderTask

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
