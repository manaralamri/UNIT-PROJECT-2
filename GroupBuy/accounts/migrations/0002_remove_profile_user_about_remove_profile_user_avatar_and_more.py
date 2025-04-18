# Generated by Django 5.1.7 on 2025-03-19 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile_user",
            name="about",
        ),
        migrations.RemoveField(
            model_name="profile_user",
            name="avatar",
        ),
        migrations.RemoveField(
            model_name="profile_user",
            name="twitch_link",
        ),
        migrations.AddField(
            model_name="profile_user",
            name="address",
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name="profile_user",
            name="city",
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name="profile_user",
            name="phone_number",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="profile_user",
            name="postal_code",
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
