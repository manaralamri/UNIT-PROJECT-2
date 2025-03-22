# Generated by Django 5.1.7 on 2025-03-21 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_remove_product_seller"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="rating",
            field=models.SmallIntegerField(
                choices=[
                    (1, "One Start"),
                    (2, "Two Stars"),
                    (3, "Three Stars"),
                    (4, "Four Stars"),
                    (5, "Five Stars"),
                ],
                default=2,
            ),
            preserve_default=False,
        ),
    ]
