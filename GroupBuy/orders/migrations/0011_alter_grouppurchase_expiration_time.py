# Generated by Django 5.1.7 on 2025-04-07 15:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0010_alter_grouppurchase_expiration_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grouppurchase",
            name="expiration_time",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(
                    2025, 4, 7, 15, 56, 49, 614448, tzinfo=datetime.timezone.utc
                ),
                null=True,
            ),
        ),
    ]
