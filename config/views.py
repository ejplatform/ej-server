import logging

from django.contrib import auth
from django.db import IntegrityError
from django.http import Http404, HttpResponseServerError
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.conf import settings

from ej.users.models import User
from ej_conversations.models import Conversation, Vote, Category
from .forms import ProfileForm, LoginForm, RegistrationForm
from .views_utils import route, get_patterns

get_patterns = get_patterns  # don't count as an unused import
DJANGO_BACKEND = 'django.contrib.auth.backends.ModelBackend',
ALLAUTH_BACKEND = 'allauth.account.auth_backends.AuthenticationBackend'
log = logging.getLogger('ej-views')


#
# Views
#
@route('')
def index(request):
    ctx = {'conversations': Conversation.objects.all()}
    return render(request, 'pages/index.jinja2', ctx)


@route('start/')
def start(request):
    if request.user.id:
        return redirect('/conversations/')
    return redirect('/login/')


@route('login/')
def login(request):
    form = LoginForm(request.POST if request.method == 'POST' else None)
    error_msg = _('Invalid username or password')

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        email, password = data['email'], data['password']

        try:
            user = User.objects.get_by_email_or_username(email)
            user = auth.authenticate(request, username=user.username, password=password)
            log.info(f'user {user} ({email}) successfully authenticated')
            auth.login(request, user)
            if user is None:
                raise User.DoesNotExist
        except User.DoesNotExist:
            log.info(f'invalid login attempt: {email}')
            form.add_error(None, error_msg)
        else:
            return redirect(request.GET.get('next', '/'))

    ctx = dict(user=request.user, form=form)
    return render(request, 'pages/login.jinja2', ctx)


@route('logout/', login_required=True)
def start(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('/')
    return HttpResponseServerError('must use POST to logout')


@route('profile/delete/', login_required=True)
def start(request):
    ctx = dict(
        content_html='<h1>Error</h1><p>Not implemented yet!</p>'
    )
    return render(request, 'base.jinja2', ctx)


@route('register/')
def register(request):
    form = RegistrationForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        name, email, password = data['name'], data['email'], data['password']
        try:
            user = User.objects.create_simple_user(name, email, password)
            log.info(f'user {user} ({email}) successfully authenticated')
        except IntegrityError as ex:
            form.add_error(None, str(ex))
        else:
            user = auth.authenticate(request,
                                     username=user.username,
                                     password=password)
            user = auth.login(request, user, backend=DJANGO_BACKEND)
            if user:
                return redirect(request.GET.get('redirect', '/'))

    ctx = dict(user=request.user, form=form)
    return render(request, 'pages/register.jinja2', ctx)


@route('profile/', login_required=True)
def profile_detail(request):
    ctx = dict(info_tab=request.GET.get('info', 'profile'))
    return render(request, 'pages/profile-detail.jinja2', ctx)


@route('profile/edit/', login_required=True)
def profile_edit(request):
    profile = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('/profile/')
    else:
        form = ProfileForm(instance=request.user)

    ctx = dict(form=form, profile=profile)
    return render(request, 'pages/profile-edit.jinja2', ctx)


@route('conversations/<slug:slug>/')
def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)

    ctx = dict(
        category=category,
        conversations=category.conversations.all(),
    )
    return render(request, 'pages/category-detail.jinja2', ctx)


@route('conversations/<slug:category_slug>/<slug:slug>/')
def conversation_detail(request, slug, category_slug):
    conversation = get_object_or_404(Conversation, slug=slug)
    if conversation.category.slug != category_slug:
        raise Http404
    comment = conversation.get_next_comment(request.user, None)
    ctx = {
        'conversation': conversation,
        'comment': comment,
    }
    if comment and request.POST.get('action') == 'vote':
        if 'agree' in request.POST:
            comment.vote(request.user, 'agree')
        elif 'pass' in request.POST:
            comment.vote(request.user, 'skip')
        elif 'disagree' in request.POST:
            comment.vote(request.user, 'disagree')
        else:
            raise ValueError('invalid parameter')

    elif request.POST.get('action') == 'comment':
        comment = request.POST['comment'].strip()
        conversation.create_comment(request.user, comment)

    return render(request, 'pages/conversation-detail.jinja2', ctx)


@route('conversations/<slug:category_slug>/<slug:slug>/info/')
def conversation_info(request, slug, category_slug):
    conversation = get_object_or_404(Conversation, slug=slug)
    if conversation.category.slug != category_slug:
        raise Http404
    ctx = dict(
        conversation=conversation,
        info=conversation.get_statistics(),
    )
    return render(request, 'pages/conversation-info.jinja2', ctx)


@route('conversations/')
def conversation_list(request):
    ctx = {'conversations': Conversation.objects.all()}
    return render(request, 'pages/conversation-list.jinja2', ctx)


@route('groups/')
def start(request):
    ctx = dict(
        content_html='<h1>Error</h1><p>Not implemented yet!</p>'
    )
    return render(request, 'base.jinja2', ctx)


#
# Debug routes
#
@route('debug/styles/')
def display(request):
    return render(request, 'pages/debug-styles.jinja2', {})


#
# Static pages
#
route('rocket/', name='rocket', template_name='pages/rocket.jinja2')
route('menu/', name='menu', template_name='pages/menu.jinja2')
route('tour/', name='tour', template_name='pages/tour.jinja2')
route('comments/', name='comments', template_name='pages/comments.jinja2')
route('notifications/', name='notifications', template_name='pages/notifications.jinja2')
