# Generated by Django 5.1.7 on 2025-03-23 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_remove_grouppurchase_participants_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="grouppurchase",
            name="participants",
        ),
        migrations.AddField(
            model_name="grouppurchase",
            name="participants",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
