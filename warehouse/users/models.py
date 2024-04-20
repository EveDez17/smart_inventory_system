#USER SETUP TO LOGIN

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from warehouse.users.utils import send_admin_approval_request
from warehouse.users.managers import UserManager

class User(AbstractUser):
    username = None  # We're using email instead of username
    email = models.EmailField(_('email address'), unique=True)
    is_approved = models.BooleanField(default=False)  # Field to track approval status
    
    class Role(models.TextChoices):
        DEFAULT_USER = "DEFAULT_USER", _('Default User')
        SECURITY = "SECURITY", _('Security')
        RECEPTIONIST = "RECEPTIONIST", _('Receptionist')
        WAREHOUSE_OPERATIVE = "WAREHOUSE_OPERATIVE", _('Warehouse Operative')
        WAREHOUSE_ADMIN = "WAREHOUSE_ADMIN", _('Warehouse Admin')
        WAREHOUSE_TEAM_LEADER = "WAREHOUSE_TEAM_LEADER", _('Warehouse Team Leader')
        WAREHOUSE_MANAGER = "WAREHOUSE_MANAGER", _('Warehouse Manager')
        INVENTORY_ADMIN = "INVENTORY_ADMIN", _('Inventory Admin')
        INVENTORY_TEAM_LEADER = "INVENTORY_TEAM_LEADER", _('Inventory Team Leader')
        INVENTORY_MANAGER = "INVENTORY_MANAGER", _('Inventory Manager')
        OPERATIONAL_MANAGER = "OPERATIONAL_MANAGER", _('Operational Manager')

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.DEFAULT_USER, verbose_name=_('Role'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    def has_role(self, role):
        return self.role == role

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if this is a new object being created
            self.is_active = False  # Do not activate on save, wait for approval
        super().save(*args, **kwargs)
        # If a specific role requires admin approval, you might adjust the logic here
        if not self.is_approved and self.role in [self.Role.WAREHOUSE_ADMIN, self.Role.OPERATIONAL_MANAGER]:
            send_admin_approval_request(self)  # Calling the function when needed
        super().save(*args, **kwargs)

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=255, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=255, verbose_name=_('Last Name'))
    dob = models.DateField(verbose_name=_('Date of Birth'))
    personal_email = models.EmailField(unique=True, verbose_name=_('Personal Email'))
    contact_number = models.CharField(max_length=20, verbose_name=_('Contact Number'))
    address = models.TextField(verbose_name=_('Address'))  # Assuming you have Address as a model or change to appropriate field type
    position = models.CharField(max_length=100, verbose_name=_('Position'))
    start_date = models.DateField(verbose_name=_('Start Date'))

    class Meta:
        db_table = 'employee'
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"