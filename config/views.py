from django.http import Http404
from django.shortcuts import render, get_object_or_404
from ej_conversations.models import Conversation, Vote, Category

from .views_utils import route, get_patterns
from .forms import ProfileForm, LoginForm, RegistrationForm


#
# Views
#
@route('login/')
def login(request):
    data = request.POST if request.method == 'POST' else None
    login_form = LoginForm(data)
    registration_form = RegistrationForm(data)
    ctx = {'user': request.user, 'login_form': login_form, 'registration_form': registration_form}
    return render(request, 'pages/login.jinja2', ctx)


@route('conversations/<slug:slug>/')
def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)

    ctx = dict(
        category=category,
        conversations=category.conversations.all(),
    )
    return render(request, 'pages/category-detail.jinja2', ctx)


@route('conversations/<slug:category_slug>/<slug:slug>')
def conversation_detail(request, slug, category_slug):
    conversation = get_object_or_404(Conversation, slug=slug)
    if conversation.category.slug != category_slug:
        raise Http404
    comment = conversation.get_next_comment(request.user, None)
    ctx = {
        'conversation': conversation,
        'comment': comment,
    }
    if comment and request.method == 'POST':
        if 'vote' in request.POST:
            if 'agree' in request.POST:
                comment.vote(request.user, Vote.AGREE)
            elif 'pass' in request.POST:
                comment.vote(request.user, Vote.PASS)
            elif 'disagree' in request.POST:
                comment.vote(request.user, Vote.DISAGREE)
            else:
                raise ValueError('invalid parameter')
        elif 'comment' in request.POST:
            conversation.create_comment(request.user, request.POST['text'])
    return render(request, 'pages/conversation-detail.jinja2', ctx)


@route('conversations/')
def conversation_list(request):
    ctx = {'conversations': Conversation.objects.all()}
    return render(request, 'pages/conversation-list.jinja2', ctx)


@route('')
def index(request):
    ctx = {'conversations': Conversation.objects.all()}
    return render(request, 'pages/index.jinja2', ctx)


@route('profile/')
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm()

    ctx = dict(
        profile_form=form,
    )
    return render(request, 'pages/profile.jinja2', ctx)


#
# Static pages
#
route('rocket/', name='rocket', template_name='pages/rocket.jinja2')
route('faq/', name='faq', template_name='pages/faq.jinja2')
route('about/', name='about', template_name='pages/about.jinja2')
route('usage/', name='usage', template_name='pages/usage.jinja2')
route('tour/', name='tour', template_name='pages/tour.jinja2')
route('comments/', name='comments', template_name='pages/comments.jinja2')
route('notifications/', name='notifications', template_name='pages/notifications.jinja2')
