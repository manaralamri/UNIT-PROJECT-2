# Generated by Django 5.1.7 on 2025-04-08 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0020_remove_product_brand_delete_brand"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="brand",
            field=models.CharField(default=2, max_length=225),
            preserve_default=False,
        ),
    ]
