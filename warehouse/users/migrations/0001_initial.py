# Generated by Django 5.0.3 on 2024-04-20 16:27

import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import warehouse.users.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("department_name", models.CharField(max_length=255)),
                ("location", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role_title",
                    models.CharField(
                        choices=[
                            ("WAREHOUSE_COMMON", "Warehouse Common"),
                            ("GATEHOUSE", "Gatehouse"),
                            ("RECEPTIONIST", "Receptionist"),
                            ("WAREHOUSE_OPERATIVE", "Warehouse Operative"),
                            ("WAREHOUSE_ADMIN", "Warehouse Admin"),
                            ("WAREHOUSE_TEAM_LEADER", "Warehouse Team Leader"),
                            ("WAREHOUSE_MANAGER", "Warehouse Manager"),
                            ("INVENTORY_ADMIN", "Inventory Admin"),
                            ("INVENTORY_TEAM_LEADER", "Inventory Team Leader"),
                            ("INVENTORY_MANAGER", "Inventory Manager"),
                            ("OPERATIONAL_MANAGER", "Operational Manager"),
                        ],
                        default="WAREHOUSE_COMMON",
                        max_length=100,
                        verbose_name="Role Title",
                    ),
                ),
                ("role_description", models.TextField(verbose_name="Role Description")),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("is_approved", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", warehouse.users.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("employee_first_name", models.CharField(max_length=100)),
                ("employee_last_name", models.CharField(max_length=100)),
                ("employee_street_number", models.CharField(max_length=128)),
                ("employee_street_name", models.CharField(max_length=255)),
                ("employee_city", models.CharField(max_length=255)),
                ("employee_county", models.CharField(max_length=255)),
                ("employee_country", models.CharField(max_length=255)),
                ("employee_post_code", models.CharField(max_length=20, unique=True)),
                ("date_hired", models.DateField(default=django.utils.timezone.now)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="employee_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="employees",
                        to="users.role",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="employee",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_profile",
                to="users.employee",
            ),
        ),
        migrations.CreateModel(
            name="EmployeeRole",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("assigned_date", models.DateField()),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="users.employee"
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="users.role"
                    ),
                ),
            ],
        ),
    ]
