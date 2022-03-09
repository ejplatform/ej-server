# Generated by Django 3.2 on 2021-10-28 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ej_users', '0004_user_signature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='signature',
            field=models.CharField(choices=[('listen_to_community', 'Listen to community'), ('listen_to_city', 'Listen to city')], default='listen_to_community', help_text='User signature', max_length=50, verbose_name='Signature'),
        ),
    ]