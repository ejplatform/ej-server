# Generated by Django 2.0.8 on 2018-09-18 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ej_users', '0001_first_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_token',
            field=models.CharField(max_length=50, null=True, unique=True, verbose_name='user token'),
        ),
    ]