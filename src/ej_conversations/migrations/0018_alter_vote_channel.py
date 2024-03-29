# Generated by Django 3.2 on 2022-01-20 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ej_conversations', '0017_vote_analytics_utm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='channel',
            field=models.CharField(choices=[('telegram', 'Telegram'), ('twilio', 'Whatsapp'), ('rasa', 'RASAX'), ('opinion_component', 'Opinion Component'), ('socketio', 'Rasa webchat'), ('ej', 'EJ'), ('unknown', 'Unknown')], default='unknown', help_text='From which EJ channel the vote comes from', max_length=50, verbose_name='Channel'),
        ),
    ]
