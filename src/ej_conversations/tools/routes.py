import json
from boogie.router import Router
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from .utils import npm_version
from .forms import RasaConversationForm, ConversationComponentForm, ConversationComponent, MailingToolForm

from .. import models
from ..tools.table import Tools

app_name = "ej_conversations_tools"
urlpatterns = Router(
    template="ej_conversations_tools/{name}.jinja2", models={"conversation": models.Conversation}
)
conversation_tools_url = f"<model:conversation>/<slug:slug>/tools"


@urlpatterns.route(conversation_tools_url)
def index(request, conversation, slug, npm=npm_version):
    tools = Tools(conversation)
    return {
        "tools": tools.list(),
        "conversation": conversation
    }


@urlpatterns.route(conversation_tools_url + "/mailing")
def mailing(request, conversation, slug):
    from .mailing import TemplateGenerator
    template = None
    form = MailingToolForm(request.POST, conversation_id=conversation)
    if request.method == "POST" and form.is_valid():
        generator = TemplateGenerator(conversation, request, "mautic")
        generator.set_custom_values(form.cleaned_data['custom_title'], form.cleaned_data['custom_comment'])
        template = generator.get_template()
        if 'download' in request.POST:
            response = HttpResponse(template, content_type="text/html")
            response['Content-Disposition'] = 'attachment; filename=template.html'
            return response
        if 'preview' in request.POST:
            template = json.dumps(template, ensure_ascii=False)
    tools = Tools(conversation)
    return {"conversation": conversation, "tool": tools.get(_('Mailing campaign')),
            "template_preview": template, "form": form}


@urlpatterns.route(conversation_tools_url + "/opinion-component")
def opinion_component(request, conversation, slug):
    from django.conf import settings
    schema = 'https' if settings.ENVIRONMENT != 'local' else 'http'
    form = ConversationComponentForm(request.POST)
    conversation_component = ConversationComponent(form)
    tools = Tools(conversation)

    return {"schema": schema,
            "tool": tools.get(_('Opinion component')),
            "npm_version": npm_version(),
            "conversation": conversation,
            "form": form,
            "conversation_component": conversation_component,
            }


@urlpatterns.route(conversation_tools_url + "/rasa")
def rasa(request, conversation, slug):
    form = RasaConversationForm(request=request, conversation=conversation)
    if form.is_valid_post():
        form.save()
        form = RasaConversationForm(conversation=conversation)

    connections = models.RasaConversation.objects.filter(conversation=conversation)
    tools = Tools(conversation)
    return {"conversation": conversation, "connections": connections, "tool": tools.get(_('Rasa chatbot')), "form": form}
