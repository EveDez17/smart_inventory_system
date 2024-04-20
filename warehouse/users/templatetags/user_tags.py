from django import template
from django.conf import settings

from warehouse.users.models import User

register = template.Library()

@register.filter(name='can_approve')
def can_approve(user):
    return user.is_superuser or user.role in {User.Role.WAREHOUSE_MANAGER, User.Role.WAREHOUSE_TEAM_LEADER}
