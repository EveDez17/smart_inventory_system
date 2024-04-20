from typing import Any
from django.core.management import call_command

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        call_command("makemigrations")
        call_command("migrate")
        call_command("loaddata", "db_category_fixture.json")
        call_command("loaddata", "db_address_fixture.json")
        call_command("loaddata", "db_supplier_fixture.json")
        call_command("loaddata", "db_foodproduct_fixture.json")
        
        