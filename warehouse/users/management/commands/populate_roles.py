# In your_app/management/commands/populate_roles.py

import warnings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from warehouse.users.models import Role

class Command(BaseCommand):
    help = 'Populate roles in the database'

    def handle(self, *args, **options):
        roles = [
            {
                'title': Role.RoleChoices.WAREHOUSE_COMMON,
                'description': 'Warehouse Common Role Description'
            },
            {
                'title': Role.RoleChoices.GATEHOUSE,
                'description': 'Gatehouse Role Description'
            },
            {
                'title': Role.RoleChoices.RECEPTIONIST,
                'description': 'Receptionist Role Description'
            },
            {
                'title': Role.RoleChoices.WAREHOUSE_OPERATIVE,
                'description': 'Warehouse Operative Role Description'
            },
            {
                'title': Role.RoleChoices.WAREHOUSE_ADMIN,
                'description': 'Warehouse Admin Role Description'
            },
            {
                'title': Role.RoleChoices.WAREHOUSE_TEAM_LEADER,
                'description': 'Warehouse Team Leader Role Description'
            },
            {
                'title': Role.RoleChoices.WAREHOUSE_MANAGER,
                'description': 'Warehouse Manager Role Description'
            },
            {
                'title': Role.RoleChoices.INVENTORY_ADMIN,
                'description': 'Inventory Admin Role Description'
            },
            {
                'title': Role.RoleChoices.INVENTORY_TEAM_LEADER,
                'description': 'Inventory Team Leader Role Description'
            },
            {
                'title': Role.RoleChoices.INVENTORY_MANAGER,
                'description': 'Inventory Manager Role Description'
            },
            {
                'title': Role.RoleChoices.OPERATIONAL_MANAGER,
                'description': 'Operational Manager Role Description'
            },
        ]

        for role_data in roles:
            try:
                Role.objects.create(role_title=role_data['title'], role_description=role_data['description'])
            except Exception as e:
                warnings.warn(f"Failed to create role: {role_data['title']}. Error: {str(e)}", Warning)

        self.stdout.write(self.style.SUCCESS('Roles successfully populated'))

        self.stdout.write(self.style.SUCCESS('Roles successfully populated'))

