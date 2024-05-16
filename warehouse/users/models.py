#USER SETUP TO LOGIN
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from warehouse.users.managers import UserManager # Importing the custom user manager

# Department model

class Department(models.Model):
    department_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.department_name

# Role model

class Role(models.Model):
    # Choices for role titles
    class RoleChoices(models.TextChoices):
        WAREHOUSE_COMMON = "WAREHOUSE_COMMON", _('Warehouse Common')
        GATEHOUSE = "GATEHOUSE", _('Gatehouse')
        RECEPTIONIST = "RECEPTIONIST", _('Receptionist')
        WAREHOUSE_OPERATIVE = "WAREHOUSE_OPERATIVE", _('Warehouse Operative')
        WAREHOUSE_ADMIN = "WAREHOUSE_ADMIN", _('Warehouse Admin')
        WAREHOUSE_TEAM_LEADER = "WAREHOUSE_TEAM_LEADER", _('Warehouse Team Leader')
        WAREHOUSE_MANAGER = "WAREHOUSE_MANAGER", _('Warehouse Manager')
        INVENTORY_ADMIN = "INVENTORY_ADMIN", _('Inventory Admin')
        INVENTORY_TEAM_LEADER = "INVENTORY_TEAM_LEADER", _('Inventory Team Leader')
        INVENTORY_MANAGER = "INVENTORY_MANAGER", _('Inventory Manager')
        OPERATIONAL_MANAGER = "OPERATIONAL_MANAGER", _('Operational Manager')

    role_title = models.CharField(
        max_length=100,
        choices=RoleChoices.choices,
        default=RoleChoices.WAREHOUSE_COMMON,
        verbose_name=_("Role Title")
    )
    role_description = models.TextField(verbose_name=_("Role Description"))

    def __str__(self):
        return self.get_role_title_display()
    
# Custom User model

class User(AbstractUser):
    # One-to-one relationship with Employee model
    employee = models.OneToOneField('Employee', on_delete=models.CASCADE, related_name='user_profile', null=True, blank=True)

    is_approved = models.BooleanField(default=False)

    objects = UserManager()  # Using the custom user manager
    
     # Method to get the absolute URL of the user

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def __str__(self):
        if self.employee:
            return f"{self.employee.employee_first_name} {self.employee.employee_last_name} ({self.username})"
        return self.username
    
# Employee model

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')  # Adjusted related_name
    employee_first_name = models.CharField(max_length=100)
    employee_last_name = models.CharField(max_length=100)
    employee_street_number = models.CharField(max_length=128)
    employee_street_name = models.CharField(max_length=255)
    employee_city = models.CharField(max_length=255)
    employee_county = models.CharField(max_length=255)
    employee_country = models.CharField(max_length=255)
    employee_post_code = models.CharField(max_length=20, unique=True)
    date_hired = models.DateField(default=timezone.now) 
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee_first_name} {self.employee_last_name}"
    
# EmployeeRole model
    
class EmployeeRole(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_date = models.DateField()  
    

