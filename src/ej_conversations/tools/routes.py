import json
from boogie.router import Router
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.shortcuts import redirect
from .utils import npm_version
from .forms import RasaConversationForm, ConversationComponentForm, ConversationComponent, MailingToolForm
from .models import RasaConversation
from .. import models
from ..tools.table import Tools


app_name = "ej_conversations_tools"
urlpatterns = Router(
    template="ej_conversations_tools/{name}.jinja2",
    models={"conversation": models.Conversation, "connection": RasaConversation},
)
conversation_tools_url = f"<model:conversation>/<slug:slug>/tools"


@urlpatterns.route(conversation_tools_url)
def index(request, conversation, slug, npm=npm_version):
    tools = Tools(conversation)
    return {"tools": tools.list(), "conversation": conversation}


@urlpatterns.route(conversation_tools_url + "/mailing")
def mailing(request, conversation, slug):
    from .mailing import TemplateGenerator

    template = None
    form = MailingToolForm(request.POST, conversation_id=conversation)
    if request.method == "POST" and form.is_valid():
        form_data = form.cleaned_data
        generator = TemplateGenerator(conversation, request, form_data["template_type"], form_data["theme"])
        generator.set_custom_values(form_data["custom_title"], form_data["custom_comment"])
        template = generator.get_template()
        if "download" in request.POST:
            response = HttpResponse(template, content_type="text/html")
            response["Content-Disposition"] = "attachment; filename=template.html"
            return response
        if "preview" in request.POST:
            template = json.dumps(template, ensure_ascii=False)
    tools = Tools(conversation)
    return {
        "conversation": conversation,
        "tool": tools.get(_("Mailing campaign")),
        "template_preview": template,
        "form": form,
    }


@urlpatterns.route(conversation_tools_url + "/opinion-component")
def opinion_component(request, conversation, slug):
    from django.conf import settings

    schema = "https" if settings.ENVIRONMENT != "local" else "http"
    form = ConversationComponentForm(request.POST)
    conversation_component = ConversationComponent(form)
    tools = Tools(conversation)

    return {
        "schema": schema,
        "tool": tools.get(_("Opinion component")),
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
    return {
        "conversation": conversation,
        "connections": connections,
        "tool": tools.get(_("Rasa chatbot")),
        "form": form,
    }


@urlpatterns.route(conversation_tools_url + "/rasa/delete/<model:connection>")
def delete_connection(request, conversation, slug, connection):
    user = request.user

    if user.is_staff or user.is_superuser or connection.conversation.author.id == user.id:
        connection.delete()
    elif connection.conversation.author.id != user.id:
        raise PermissionError("cannot delete connection from another user")
    else:
        raise PermissionError("user is not allowed to delete connections")

    return redirect(conversation.url("conversation-tools:rasa"))
