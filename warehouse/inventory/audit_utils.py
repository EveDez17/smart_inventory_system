from django.contrib.contenttypes.models import ContentType
from warehouse.inventory.models import AuditLog, User, LLOPTask, FoodProduct

def log_audit_action(instance, action, user, description):
    """
    Generic function to log audit actions for any model instance.
    Parameters:
        instance (models.Model): The Django model instance to log.
        action (str): The action performed (from AuditLog.ACTION_CHOICES).
        user (User): The user who performed the action.
        description (str): A descriptive message about the action.
    """
    AuditLog.objects.create(
        content_object=instance,
        action=action,
        user=user,
        description=description
    )

def log_llop_task_start(task_id, username, description):
    """
    Convenience function specifically for starting LLOPTasks.
    """
    llop_task = LLOPTask.objects.get(id=task_id)
    user = User.objects.get(username=username)
    log_audit_action(llop_task, 'Start', user, description)

def log_food_product_update(sku, username, description):
    """
    Convenience function specifically for updating FoodProducts.
    """
    food_product = FoodProduct.objects.get(sku=sku)
    user = User.objects.get(username=username)
    log_audit_action(food_product, 'Update', user, description)
