import json
from boogie.router import Router
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.shortcuts import redirect
from .utils import npm_version, user_can_add_new_domain
from .forms import (
    RasaConversationForm,
    ConversationComponentForm,
    ConversationComponent,
    MailingToolForm,
    MauticConversationForm,
)
from .models import RasaConversation, ConversationMautic
from .. import models
from ..tools.table import Tools


app_name = "ej_conversations_tools"
urlpatterns = Router(
    template="ej_conversations_tools/{name}.jinja2",
    models={
        "conversation": models.Conversation,
        "connection": RasaConversation,
        "mautic_connection": ConversationMautic,
    },
)
conversation_tools_url = f"<model:conversation>/<slug:slug>/tools"


@urlpatterns.route(conversation_tools_url)
def index(request, conversation, slug, npm=npm_version):
    tools = Tools(conversation)
    return {"tools": tools.list(), "conversation": conversation}


@urlpatterns.route(conversation_tools_url + "/mailing")
def mailing(request, conversation, slug):
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
    user = request.user
    user_can_add = user_can_add_new_domain(user, conversation)

    if form.is_valid_post() and user_can_add:
        form.save()
        form = RasaConversationForm(conversation=conversation)
    elif form.is_valid_post() and not user_can_add:
        raise PermissionError("user is not allowed to create conversation rasa connections")

    conversation_rasa_connections = models.RasaConversation.objects.filter(conversation=conversation)
    tools = Tools(conversation)
    return {
        "conversation": conversation,
        "conversation_rasa_connections": conversation_rasa_connections,
        "tool": tools.get(_("Rasa Webchat")),
        "form": form,
        "is_valid_user": user_can_add,
    }


@urlpatterns.route(conversation_tools_url + "/rasa/delete/<model:connection>")
def delete_connection(request, conversation, slug, connection):
    user = request.user

    if user.is_staff or user.is_superuser or connection.conversation.author.id == user.id:
        connection.delete()
    elif connection.conversation.author.id != user.id:
        raise PermissionError("cannot delete conversation rasa connections from another user")
    else:
        raise PermissionError("user is not allowed to delete conversation rasa connections")

    return redirect(conversation.url("conversation-tools:rasa"))


@urlpatterns.route(
    conversation_tools_url + "/mautic", perms=["ej.can_access_mautic_connection:conversation"]
)
def mautic(request, conversation, slug):
    tools = Tools(conversation)
    conversation_kwargs = {
        "conversation": conversation,
    }
    form = MauticConversationForm(request=request, initial=conversation_kwargs)
    connections = models.ConversationMautic.objects.filter(conversation=conversation)
    if request.method == "POST":
        if form.is_valid():
            form.save()
    return {
        "conversation": conversation,
        "connections": connections,
        "tool": tools.get(_("Mautic")),
        "form": form,
    }


@urlpatterns.route(
    conversation_tools_url + "/mautic/delete/<model:mautic_connection>",
    perms=["ej.can_access_mautic_connection:conversation"],
)
def delete_mautic_connection(request, conversation, slug, mautic_connection):
    mautic_connection.delete()
    return redirect(conversation.url("conversation-tools:mautic"))


@urlpatterns.route(conversation_tools_url + "/mautic/create_contact/<model:mautic_connection>")
def create_mautic_contact(
    request, conversation, slug, mautic_connection, oauth_token_secret, oauth_verifier
):
    # request.post(rota  de contato, payload, token?)

    pass
