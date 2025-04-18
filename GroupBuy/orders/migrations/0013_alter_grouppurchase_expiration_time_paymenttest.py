# Generated by Django 5.1.7 on 2025-04-08 14:58

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0012_alter_grouppurchase_expiration_time"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="grouppurchase",
            name="expiration_time",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2025, 4, 8, 14, 59, 10, 57991, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="PaymentTest",
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
                ("name", models.CharField(max_length=250)),
                ("email", models.EmailField(max_length=254)),
                ("address", models.CharField(blank=True, max_length=250)),
                ("postal_code", models.CharField(blank=True, max_length=10)),
                ("phone_number", models.CharField(blank=True, max_length=20)),
                ("city", models.CharField(blank=True, max_length=250)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "group_purchase",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="orders.grouppurchase",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="orders.order"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
