# Generated by Django 2.1.2 on 2018-11-08 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ej_profiles", "0002_add_state_field")]

    operations = [
        migrations.RemoveField(model_name="profile", name="image"),
        migrations.AddField(
            model_name="profile",
            name="profile_photo",
            field=models.ImageField(
                blank=True, null=True, upload_to="profile_images", verbose_name="Profile Photo"
            ),
        ),
    ]
