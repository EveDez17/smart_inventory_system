# Generated by Django 5.0.3 on 2024-04-22 18:21

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("outbound", "0001_initial"),
        ("storage", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Outbound",
            fields=[
                (
                    "location_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="storage.location",
                    ),
                ),
                ("address", models.CharField(max_length=255, null=True)),
                ("floor_number", models.PositiveIntegerField()),
                ("bay_number", models.PositiveIntegerField()),
                ("additional_info", models.TextField()),
                ("location_identifier", models.CharField(max_length=100)),
                ("max_capacity", models.IntegerField()),
                ("operational_restrictions", models.CharField(max_length=255)),
                ("special_handling_required", models.BooleanField(default=False)),
                (
                    "outbound_code",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Outbound Code"
                    ),
                ),
                (
                    "utilized_capacity",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Utilized Capacity"
                    ),
                ),
            ],
            bases=("storage.location",),
        ),
        migrations.CreateModel(
            name="ProductLocation",
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
                    "quantity",
                    models.PositiveIntegerField(
                        default=0, help_text="Quantity of the product at the location."
                    ),
                ),
            ],
            options={
                "verbose_name": "Product Location",
                "verbose_name_plural": "Product Locations",
            },
        ),
        migrations.CreateModel(
            name="ReplenishmentPickingTask",
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
                ("quantity", models.PositiveIntegerField()),
                (
                    "vna_equipment",
                    models.CharField(
                        help_text="VNA equipment used for the task.",
                        max_length=255,
                        verbose_name="VNA Equipment",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("In Progress", "In Progress"),
                            ("Completed", "Completed"),
                        ],
                        default="Pending",
                        max_length=20,
                    ),
                ),
                ("start_time", models.DateTimeField(default=django.utils.timezone.now)),
                ("completion_time", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Replenishment Picking Task",
                "verbose_name_plural": "Replenishment Picking Tasks",
            },
        ),
        migrations.CreateModel(
            name="ReplenishmentRequest",
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
                ("required_quantity", models.PositiveIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Requested", "Requested"),
                            ("Fulfilling", "Fulfilling"),
                            ("Completed", "Completed"),
                        ],
                        default="Requested",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="ReplenishmentTask",
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
                    "quantity",
                    models.PositiveIntegerField(
                        help_text="Quantity to be replenished."
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("In Progress", "In Progress"),
                            ("Completed", "Completed"),
                        ],
                        default="Pending",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.IntegerField(
                        default=0,
                        help_text="Priority of the task, with higher numbers indicating higher priority.",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Shipment",
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
                    "shipment_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Shipment Time"
                    ),
                ),
                (
                    "tracking_number",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Tracking Number",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VNATask",
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
                    "task_type",
                    models.CharField(
                        choices=[
                            ("Putaway", "Putaway from PND to Storage"),
                            ("Order Picking", "Order Picking from Storage to PND"),
                            (
                                "Replenishment Picking",
                                "Replenishment Picking from Storage to PND",
                            ),
                        ],
                        default="Putaway",
                        help_text="Type of VNA task.",
                        max_length=30,
                    ),
                ),
                ("quantity", models.PositiveIntegerField(verbose_name="Quantity")),
                (
                    "vna_equipment",
                    models.CharField(
                        help_text="The VNA equipment used for this task.",
                        max_length=255,
                        verbose_name="VNA Equipment",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Assigned", "Assigned"),
                            ("In Progress", "In Progress"),
                            ("Completed", "Completed"),
                        ],
                        default="Assigned",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="Start Time"),
                ),
                (
                    "completion_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Completion Time"
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, null=True, verbose_name="Notes"),
                ),
            ],
            options={
                "verbose_name": "VNATask",
                "verbose_name_plural": "VNATasks",
            },
        ),
    ]
