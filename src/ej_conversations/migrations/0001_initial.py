# Generated by Django 2.2.2 on 2019-06-06 03:54

import autoslug.fields
import boogie.fields.enum_field
import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import ej_conversations.enums
import ej_conversations.validators
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('status', model_utils.fields.StatusField(choices=[('pending', 'awaiting moderation'), ('approved', 'approved'), ('rejected', 'rejected')], default='pending', max_length=100, no_check_for_status=True, verbose_name='status')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('content', models.TextField(help_text='Body of text for the comment', max_length=252, validators=[django.core.validators.MinLengthValidator(2), ej_conversations.validators.is_not_empty], verbose_name='Content')),
                ('rejection_reason', boogie.fields.enum_field.EnumField(ej_conversations.enums.RejectionReason, default=ej_conversations.enums.RejectionReason(0), verbose_name='Rejection reason')),
                ('rejection_reason_text', models.TextField(blank=True, help_text='You must provide a reason to reject a comment. Users will receive this feedback.', verbose_name='Rejection reason (free-form)')),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(help_text='Short description used to create URL slugs (e.g. School system).', max_length=255, verbose_name='Title')),
                ('text', models.TextField(help_text='What do you want to ask?', verbose_name='Question')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='title')),
                ('is_promoted', models.BooleanField(default=False, help_text='Promoted conversations appears in the main /conversations/ endpoint.', verbose_name='Promote conversation?')),
                ('is_hidden', models.BooleanField(default=False, help_text='Hidden conversations does not appears in boards or in the main /conversations/ endpoint.', verbose_name='Hide conversation?')),
            ],
            options={
                'ordering': ['created'],
                'permissions': (('can_publish_promoted', 'Can publish promoted conversations'), ('is_moderator', 'Can moderate comments in any conversation')),
            },
        ),
        migrations.CreateModel(
            name='ConversationTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FavoriteConversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', boogie.fields.enum_field.EnumField(ej_conversations.enums.Choice, help_text='Agree, disagree or skip', verbose_name='Choice')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
