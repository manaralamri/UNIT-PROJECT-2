# Generated by Django 5.1.7 on 2025-03-19 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_product_seller"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="seller",
        ),
    ]
