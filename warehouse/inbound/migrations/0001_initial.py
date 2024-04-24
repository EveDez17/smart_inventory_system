# Generated by Django 5.0.3 on 2024-04-22 18:21

import django.utils.timezone
import simple_history.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FinalBayAssignment",
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
                ("final_bay", models.CharField(max_length=50)),
                (
                    "confirmed_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "is_loaded",
                    models.BooleanField(
                        default=False, verbose_name="Loading Confirmed"
                    ),
                ),
                (
                    "loaded_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Loaded At"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FLTTask",
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
                            ("Putaway", "Putaway from Inbound to PND"),
                            (
                                "Order Completion",
                                "Full Pallets Order Completion to Outbound",
                            ),
                            ("Replenishment", "Replenishment to Pick Faces"),
                        ],
                        default="Putaway",
                        help_text="Type of FLT task.",
                        max_length=30,
                    ),
                ),
                ("quantity", models.PositiveIntegerField()),
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
        ),
        migrations.CreateModel(
            name="GatehouseBooking",
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
                ("driver_name", models.CharField(max_length=255)),
                ("company", models.CharField(max_length=255)),
                ("vehicle_registration", models.CharField(max_length=50)),
                (
                    "trailer_number",
                    models.CharField(max_length=50, verbose_name="Trailer Number"),
                ),
                (
                    "arrival_time",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("has_paperwork", models.BooleanField(default=False)),
                ("paperwork_description", models.CharField(blank=True, max_length=255)),
                ("cancelled", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalFinalBayAssignment",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("final_bay", models.CharField(max_length=50)),
                (
                    "confirmed_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "is_loaded",
                    models.BooleanField(
                        default=False, verbose_name="Loading Confirmed"
                    ),
                ),
                (
                    "loaded_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Loaded At"
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical final bay assignment",
                "verbose_name_plural": "historical final bay assignments",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalFLTTask",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "task_type",
                    models.CharField(
                        choices=[
                            ("Putaway", "Putaway from Inbound to PND"),
                            (
                                "Order Completion",
                                "Full Pallets Order Completion to Outbound",
                            ),
                            ("Replenishment", "Replenishment to Pick Faces"),
                        ],
                        default="Putaway",
                        help_text="Type of FLT task.",
                        max_length=30,
                    ),
                ),
                ("quantity", models.PositiveIntegerField()),
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
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical flt task",
                "verbose_name_plural": "historical flt tasks",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalGatehouseBooking",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("driver_name", models.CharField(max_length=255)),
                ("company", models.CharField(max_length=255)),
                ("vehicle_registration", models.CharField(max_length=50)),
                (
                    "trailer_number",
                    models.CharField(max_length=50, verbose_name="Trailer Number"),
                ),
                (
                    "arrival_time",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("has_paperwork", models.BooleanField(default=False)),
                ("paperwork_description", models.CharField(blank=True, max_length=255)),
                ("cancelled", models.BooleanField(default=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical gatehouse booking",
                "verbose_name_plural": "historical gatehouse bookings",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalInbound",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(verbose_name="quantity received"),
                ),
                (
                    "receiving_date",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="receiving date"
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True, null=True, verbose_name="additional notes"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending Release"),
                            ("Received", "Received"),
                            ("Released", "Released for Putaway"),
                            ("Stored", "Stored"),
                        ],
                        default="Pending",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "floor_location",
                    models.CharField(
                        help_text="Location on the warehouse floor where the stock is placed",
                        max_length=100,
                        verbose_name="Floor Location",
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Inbound Record",
                "verbose_name_plural": "historical Inbound Records",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalProvisionalBayAssignment",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("provisional_bay", models.CharField(max_length=50)),
                (
                    "assigned_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical provisional bay assignment",
                "verbose_name_plural": "historical provisional bay assignments",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalPutawayTask",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
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
                    models.DateTimeField(
                        blank=True, editable=False, verbose_name="Start Time"
                    ),
                ),
                (
                    "completion_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Completion Time"
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical putaway task",
                "verbose_name_plural": "historical putaway tasks",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalReceiving",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(
                        help_text="Enter quantity of product received",
                        verbose_name="quantity received",
                    ),
                ),
                (
                    "receiving_date",
                    models.DateField(
                        default=django.utils.timezone.now,
                        help_text="Date when product was received",
                        verbose_name="receiving date",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Any additional notes about the receiving",
                        null=True,
                        verbose_name="additional notes",
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Receiving",
                "verbose_name_plural": "historical Receivings",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Inbound",
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
                    models.PositiveIntegerField(verbose_name="quantity received"),
                ),
                (
                    "receiving_date",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="receiving date"
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True, null=True, verbose_name="additional notes"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending Release"),
                            ("Received", "Received"),
                            ("Released", "Released for Putaway"),
                            ("Stored", "Stored"),
                        ],
                        default="Pending",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "floor_location",
                    models.CharField(
                        help_text="Location on the warehouse floor where the stock is placed",
                        max_length=100,
                        verbose_name="Floor Location",
                    ),
                ),
            ],
            options={
                "verbose_name": "Inbound Record",
                "verbose_name_plural": "Inbound Records",
                "ordering": ["-receiving_date"],
            },
        ),
        migrations.CreateModel(
            name="ProvisionalBayAssignment",
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
                ("provisional_bay", models.CharField(max_length=50)),
                (
                    "assigned_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PutawayTask",
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
            ],
        ),
        migrations.CreateModel(
            name="Receiving",
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
                        help_text="Enter quantity of product received",
                        verbose_name="quantity received",
                    ),
                ),
                (
                    "receiving_date",
                    models.DateField(
                        default=django.utils.timezone.now,
                        help_text="Date when product was received",
                        verbose_name="receiving date",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Any additional notes about the receiving",
                        null=True,
                        verbose_name="additional notes",
                    ),
                ),
            ],
            options={
                "verbose_name": "Receiving",
                "verbose_name_plural": "Receivings",
                "ordering": ["-receiving_date"],
            },
        ),
    ]