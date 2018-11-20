# Generated by Django 2.1.2 on 2018-11-20 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ej_conversations', '0004_update_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='limit_report_users',
            field=models.PositiveIntegerField(default=0, help_text='Limit number of participants, making /reports/ route unavailable if limit is reached except for super admin.', verbose_name='Limit users'),
        ),
    ]
