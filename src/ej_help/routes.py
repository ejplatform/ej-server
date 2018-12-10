from pathlib import Path

from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_configurations import social_icons, fragment
from .forms import TalkToUsForm

app_name = 'ej_help'
urlpatterns = Router(
    template=['ej_help/{name}.jinja2', 'generic.jinja2'],
)

REPO = Path(__file__).parent.parent.parent
LIB = REPO / 'lib/resources/pages/'


def flat_pages_route(slug):
    def route(request):
        try:
            page = FlatPage.objects.get(url=f'/{slug}/')
        except FlatPage.DoesNotExist:
            page = fallback_page(slug)
        return render(request, page.template_name, {'flatpage': page})

    route.__name__ = route.__qualname__ = slug
    return route


def fallback_page(slug):
    md = LIB / f'{slug}.md'
    html = LIB / f'{slug}.html'
    if html.exists():
        data = open(html).read()
        return FlatPage(content=data, title=slug, template_name='flatpages/html.html')
    elif md.exists():
        data = open(md).read()
        return FlatPage(content=data, title=slug, template_name='flatpages/markdown.html')
    else:
        data = _('Page {slug} not found').format(slug=slug)
        return FlatPage(content=data, title=slug, template_name='flatpages/html.html')


@urlpatterns.route('start/')
def start():
    return {}


@urlpatterns.route('social/')
def social():
    return {'icons': social_icons()}


@urlpatterns.route('talk-to-us/')
def talk_to_us(request):
    thank_you_message = None

    if request.method == 'POST' and request.user.is_authenticated:
        form = TalkToUsForm(request.POST)
        if form.is_valid():
            subject = _('[EJ] {subject}').format(subject=form.cleaned_data['subject'])
            message = _('E-mail from: {email}\n\n{message}').format(
                email=request.user.email,
                message=form.cleaned_data['message'],
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )
            thank_you_message = _('Your message was successfully sent!')
            form = None
    else:
        form = TalkToUsForm()

    return {
        'fragment': fragment('help.talk-to-us', raises=False),
        'form': form,
        'can_send_form': request.user.is_authenticated,
        'thank_you_message': thank_you_message,
    }


urlpatterns.register(flat_pages_route('rules'), 'rules/')
urlpatterns.register(flat_pages_route('faq'), 'faq/')
urlpatterns.register(flat_pages_route('about-us'), 'about-us/')
urlpatterns.register(flat_pages_route('usage'), 'usage/')
