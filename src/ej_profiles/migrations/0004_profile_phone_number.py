# Generated by Django 2.2.19 on 2021-06-08 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ej_profiles", "0003_barbara_change_state_max_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="phone_number",
            field=models.CharField(blank=True, max_length=11, unique=True, verbose_name="Phone number"),
        ),
    ]