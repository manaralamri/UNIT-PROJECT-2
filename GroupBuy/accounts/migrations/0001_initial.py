# Generated by Django 5.1.7 on 2025-03-18 16:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile_Seller",
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
                    "avatar",
                    models.ImageField(
                        default="images/avatars/avatar.webp",
                        upload_to="images/avatars/",
                    ),
                ),
                ("twitch_link", models.URLField(blank=True)),
                ("CR", models.CharField(max_length=20)),
                ("CR_image", models.ImageField(upload_to="images/cr/")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Profile_User",
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
                ("about", models.TextField(blank=True)),
                (
                    "avatar",
                    models.ImageField(
                        default="images/avatars/avatar.webp",
                        upload_to="images/avatars/",
                    ),
                ),
                ("twitch_link", models.URLField(blank=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
