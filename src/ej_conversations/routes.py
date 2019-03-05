from logging import getLogger

from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import a

from boogie.models import F
from boogie.router import Router
from ej_conversations.rules import next_comment
from ej_conversations.utils import check_promoted, process_conversation_detail_post, \
    conversation_admin_menu_links
from . import forms, models
from .models import Conversation

log = getLogger('ej')

app_name = 'ej_conversations'
urlpatterns = Router(
    template='ej_conversations/{name}.jinja2',
    models={
        'conversation': models.Conversation,
        'comment': models.Comment,
    },
    lookup_field={
        'conversation': 'id',
        'comment': 'slug',
    },
    lookup_type='slug',
)
conversation_url = f'<model:conversation>/<slug:slug>/'


#
# Display conversations
#
@urlpatterns.route('', name='list')
def conversation_list(request,
                      queryset=(Conversation.objects
                          .filter(is_promoted=True, is_hidden=False)),
                      new_perm='ej.can_add_promoted_conversation',
                      perm_obj=None,
                      url=None):

    if request.user.has_perm(new_perm, perm_obj):
        url = url or reverse('conversation:create')
        menu_links = [a(_('New Conversation'), href=url)]
    else:
        menu_links = []
    return {
        'conversations': getattr(queryset, 'all', lambda: queryset)(),
        'title': _('Public conversations'),
        'subtitle': _('Participate voting and creating comments!'),
        'menu_links': menu_links,
    }


@urlpatterns.route(conversation_url, login=True)
def detail(request, conversation, slug=None, check=check_promoted, **kwargs):
    check(conversation)
    user = request.user
    if request.method == 'POST':
        process_conversation_detail_post(request, conversation)

    return {
        'conversation': conversation,
        'comment': next_comment(conversation, user),
        'menu_links': conversation_admin_menu_links(conversation, user),
        **kwargs,
    }


#
# Admin URLs
#
@urlpatterns.route('add/', perms=['ej.can_add_promoted_conversation'])
def create(request, **kwargs):
    kwargs.setdefault('is_promoted', True)
    form = forms.ConversationForm(request=request)
    if form.is_valid_post():
        with transaction.atomic():
            conversation = form.save_comments(request.user, **kwargs)
        return redirect(conversation.get_absolute_url())
    return {'form': form}


@urlpatterns.route(conversation_url + 'edit/',
                   perms=['ej.can_edit_conversation:conversation'])
def edit(request, conversation, slug=None, check=check_promoted, **kwargs):
    check(conversation)
    form = forms.ConversationForm(request=request, instance=conversation)
    can_publish = request.user.has_perm('can_publish_promoted')

    if form.is_valid_post():
        # Check if user is not trying to edit the is_promoted status without
        # permission. This is possible since the form sees this field
        # for all users and does not check if the user is authorized to
        # change is value.
        if form.cleaned_data['is_promoted'] != conversation.is_promoted:
            raise PermissionError('invalid operation')
        form.save()

        # Now we decide the correct redirect page
        page = request.POST.get('next')
        if page == 'stereotype':
            url = reverse('cluster:conversation-stereotype')
        elif page == 'moderate':
            url = reverse('conversation:moderate')
        else:
            url = conversation.get_absolute_url()
        return redirect(url)

    return {
        'conversation': conversation,
        'form': form,
        'menu_links': conversation_admin_menu_links(conversation, request.user),
        'can_publish': can_publish,
    }


@urlpatterns.route(conversation_url + 'moderate/',
                   perms=['ej.can_moderate_conversation:conversation'])
def moderate(request, conversation, slug=None, check=check_promoted):
    check(conversation)
    form = forms.ModerationForm(request=request)

    if form.is_valid_post():
        form.save()
        form = forms.ModerationForm()

    # Fetch all comments and filter
    status_filter = (lambda value: lambda x: x.status == value)
    status = models.Comment.STATUS
    comments = conversation.comments.annotate(annotation_author_name=F.author.name)

    return {
        'conversation': conversation,
        'approved': list(filter(status_filter(status.approved), comments)),
        'pending': list(filter(status_filter(status.pending), comments)),
        'rejected': list(filter(status_filter(status.rejected), comments)),
        'menu_links': conversation_admin_menu_links(conversation, request.user),
        'form': form,
    }


#
# Auxiliary functions
#
def login_link(content, obj):
    path = obj.get_absolute_url()
    return a(content, href=reverse('auth:login') + f'?next={path}')
