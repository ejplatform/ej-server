# Generated by Django 2.0.7 on 2018-07-24 13:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ej_conversations', '0009_conversationboard'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteConversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ej_conversations.Conversation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='favoriteconversation',
            unique_together={('conversation', 'user')},
        ),
    ]
