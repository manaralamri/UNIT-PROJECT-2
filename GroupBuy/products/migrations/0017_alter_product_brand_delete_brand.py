# Generated by Django 5.1.7 on 2025-04-02 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0016_brand_alter_product_brand"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="brand",
            field=models.CharField(max_length=225),
        ),
        migrations.DeleteModel(
            name="Brand",
        ),
    ]
