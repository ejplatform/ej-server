import json
import requests
from boogie.router import Router
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from .utils import npm_version, user_can_add_new_domain, prepare_host_with_https, get_host_with_protocol
from .forms import (
    RasaConversationForm,
    ConversationComponentForm,
    ConversationComponent,
    MailingToolForm,
    MauticConversationForm,
)
from ej_conversations.models import Conversation
from .models import (
    RasaConversation,
    ConversationMautic,
    MauticOauth2Service,
    MauticClient,
    ChatbotTelegramTool,
    ChatbotWhatsappTool,
)
from ej_conversations import models
from .table import Tools


app_name = "ej_tools"
urlpatterns = Router(
    template="ej_tools/{name}.jinja2",
    models={
        "conversation": Conversation,
        "connection": RasaConversation,
        "mautic_connection": ConversationMautic,
    },
)
conversation_tools_url = f"<model:conversation>/<slug:slug>/tools"
conversation_tools_chatbot_url = f"{conversation_tools_url}/chatbot"


@urlpatterns.route(conversation_tools_url, perms=["ej.can_edit_conversation:conversation"])
def index(request, board, conversation, slug, npm=npm_version):
    tools = Tools(conversation)
    return {"tools": tools.list(), "conversation": conversation}


@urlpatterns.route(conversation_tools_url + "/mailing")
def mailing(request, board, conversation, slug):
    from .mailing import TemplateGenerator

    template = "null"
    form = MailingToolForm(request.POST, conversation_id=conversation)
    if request.method == "POST" and form.is_valid():
        form_data = form.cleaned_data
        generator = TemplateGenerator(conversation, request, form_data)
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
def opinion_component(request, conversation, **kwargs):
    from django.conf import settings

    schema = "https" if settings.ENVIRONMENT != "local" else "http"
    form = ConversationComponentForm(request.POST)
    conversation_component = ConversationComponent(form)
    tools = Tools(conversation)

    if "preview" in request.POST:
        form.is_valid()
        request.session["theme"] = form.cleaned_data["theme"] or "icd"
        request.session["authentication_type"] = form.cleaned_data["authentication_type"]
        return redirect(conversation.url("conversation-tools:opinion-component-preview"))

    return {
        "schema": schema,
        "tool": tools.get(_("Opinion component")),
        "npm_version": npm_version(),
        "conversation": conversation,
        "form": form,
        "conversation_component": conversation_component,
    }


@urlpatterns.route(conversation_tools_url + "/opinion-component/preview")
def opinion_component_preview(request, board, conversation, slug):
    host = get_host_with_protocol(request)
    theme = request.session.get("theme")
    auth_type = request.session.get("authentication_type")
    return {
        "conversation": conversation,
        "authentication_type": auth_type,
        "theme": theme,
        "host": host,
    }


@urlpatterns.route(conversation_tools_url + "/chatbot")
def chatbot(request, board, conversation, slug):
    tools = Tools(conversation)
    return {
        "conversation": conversation,
        "tool": tools.get(_("Chatbot")),
    }


@urlpatterns.route(conversation_tools_url + "/telegram")
def telegram(request, board, conversation, slug):
    tools = Tools(conversation)

    return {
        "conversation": conversation,
        "tool": tools.get(_("Chatbot")),
        "channels": ChatbotTelegramTool.CHANNELS_CHOICES,
        "shareText": ChatbotTelegramTool.SHARE,
    }


@urlpatterns.route(conversation_tools_chatbot_url + "/whatsapp")
def whatsapp(request, board, conversation, slug):
    tools = Tools(conversation)
    return {
        "conversation": conversation,
        "tool": tools.get(_("Chatbot")),
        "channels": ChatbotWhatsappTool.CHANNEL_CHOICES,
        "shareText": ChatbotWhatsappTool.SHARE,
    }


@urlpatterns.route(conversation_tools_chatbot_url + "/rasa")
def rasa(request, conversation, **kwargs):
    user_can_add = user_can_add_new_domain(request.user, conversation)

    if request.method == "POST":
        form = RasaConversationForm(request.POST)
        if not user_can_add:
            raise PermissionError("user is not allowed to create conversation rasa connections")

        if form.is_valid():
            form.save()
            form = RasaConversationForm()
    else:
        form = RasaConversationForm()

    conversation_rasa_connections = models.RasaConversation.objects.filter(conversation=conversation)
    tools = Tools(conversation)
    return {
        "conversation": conversation,
        "conversation_rasa_connections": conversation_rasa_connections,
        "tool": tools.get(_("Chatbot")),
        "form": form,
        "is_valid_user": user_can_add,
    }


@urlpatterns.route(conversation_tools_chatbot_url + "/rasa/delete/<model:connection>")
def delete_connection(request, board, conversation, slug, connection):
    user = request.user

    if user.is_staff or user.is_superuser or connection.conversation.author.id == user.id:
        connection.delete()
    elif connection.conversation.author.id != user.id:
        raise PermissionError("cannot delete conversation rasa connections from another user")
    else:
        raise PermissionError("user is not allowed to delete conversation rasa connections")

    return redirect(conversation.url("conversation-tools:rasa"))


@urlpatterns.route(
    conversation_tools_chatbot_url + "/mautic", perms=["ej.can_access_mautic_connection:conversation"]
)
def mautic(request, board, conversation, slug, oauth2_code=None):
    error_message = None
    connections = None

    try:
        connections = ConversationMautic.objects.get(conversation=conversation)
        if oauth2_code:
            connections.code = oauth2_code
            connections.save()
    except Exception as e:
        print(e)

    tools = Tools(conversation)
    conversation_kwargs = {
        "conversation": conversation,
    }
    form = MauticConversationForm(request=request, initial=conversation_kwargs)
    https_ej_server = prepare_host_with_https(request)

    if request.method == "POST":
        if form.is_valid():
            conversation_mautic = form.save()
            try:
                return MauticClient.redirect_to_mautic_oauth2(https_ej_server, conversation_mautic)
            except Exception as e:
                conversation_mautic.delete()
                error_message = e.message

    if request.method == "GET" and request.GET.get("code"):
        try:
            conversation_mautic = models.ConversationMautic.objects.get(conversation_id=conversation.id)
            save_oauth2_tokens(https_ej_server, conversation_mautic, request.GET.get("code"))
        except Exception as e:
            conversation_mautic.delete()
            error_message = e.message

    return {
        "conversation": conversation,
        "connections": connections,
        "tool": tools.get(_("Mautic")),
        "form": form,
        "errors": error_message,
    }


@urlpatterns.route(
    conversation_tools_chatbot_url + "/mautic/delete/<model:mautic_connection>",
    perms=["ej.can_access_mautic_connection:conversation"],
)
def delete_mautic_connection(request, board, conversation, slug, mautic_connection):
    mautic_connection.delete()
    return redirect(conversation.url("conversation-tools:mautic"))


def save_oauth2_tokens(ej_server_url, conversation_mautic, code):
    oauth2_service = MauticOauth2Service(ej_server_url, conversation_mautic)
    oauth2_service.save_tokens(code)
