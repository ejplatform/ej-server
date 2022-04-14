import json
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.shortcuts import redirect
from .utils import (
    npm_version,
    user_can_add_new_domain,
    prepare_host_with_https,
    get_host_with_schema,
)
from django.http import HttpResponse
from .forms import (
    RasaConversationForm,
    ConversationComponentForm,
    ConversationComponent,
    MailingToolForm,
    MauticConversationForm,
)
from .models import (
    RasaConversation,
    ConversationMautic,
    MauticOauth2Service,
    MauticClient,
    WebchatHelper,
)
from ej_conversations.models import Conversation
from ej_signatures.models import SignatureFactory
from ej.decorators import can_access_tool_page, can_edit_conversation


@can_edit_conversation
def index(request, board_slug, conversation_id, slug):
    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tools = user_signature.get_conversation_tools(conversation)
    context = {"tools": tools, "conversation": conversation}
    return render(request, "ej_tools/index.jinja2", context)


@can_access_tool_page
def mailing(request, board_slug, conversation_id, slug):
    from .mailing import TemplateGenerator

    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Mailing campaign"), conversation)
    tool.raise_error_if_not_active()

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
    context = {
        "conversation": conversation,
        "tool": tool,
        "template_preview": template,
        "form": form,
    }
    return render(request, "ej_tools/mailing.jinja2", context)


@can_access_tool_page
def opinion_component(request, board_slug, conversation_id, slug):
    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Opinion component"), conversation)
    tool.raise_error_if_not_active()

    form = ConversationComponentForm(request.POST)
    conversation_component = ConversationComponent(form)
    if "preview" in request.POST:
        form.is_valid()
        theme = form.cleaned_data["theme"]
        if theme:
            theme = f"?theme={theme}"
        return redirect(conversation.patch_url("conversation-tools:opinion-component-preview") + theme)
    context = {
        "ej_domain": get_host_with_schema(request),
        "tool": tool,
        "npm_version": npm_version(),
        "conversation": conversation,
        "form": form,
        "conversation_component": conversation_component,
    }
    return render(request, "ej_tools/opinion-component.jinja2", context)


def opinion_component_preview(request, board_slug, conversation_id, slug):

    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Opinion component"), conversation)
    preview_token = tool.get_preview_token(request, conversation)
    tool.raise_error_if_not_active()
    host = get_host_with_schema(request)
    theme = request.GET.get("theme", "icd")
    context = {
        "conversation": conversation,
        "theme": theme,
        "host": host,
        "conversation_author_token": preview_token,
    }
    return render(request, "ej_tools/opinion-component-preview.jinja2", context)


@can_access_tool_page
def chatbot(request, board_slug, conversation_id, slug):
    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    context = {
        "conversation": conversation,
        "tool": user_signature.get_tool(_("Opinion Bots"), conversation),
    }
    return render(request, "ej_tools/chatbot.jinja2", context)


@can_access_tool_page
def telegram(request, board_slug, conversation_id, slug):
    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Opinion Bots"), conversation).telegram
    tool.raise_error_if_not_active()
    context = {"conversation": conversation, "tool": tool}
    return render(request, "ej_tools/telegram.jinja2", context)


@can_access_tool_page
def whatsapp(request, board_slug, conversation_id, slug):
    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Opinion Bots"), conversation).whatsapp
    tool.raise_error_if_not_active()
    context = {"conversation": conversation, "tool": tool}
    return render(request, "ej_tools/whatsapp.jinja2", context)


@can_access_tool_page
def webchat(request, board_slug, conversation_id, slug):
    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Opinion Bots"), conversation).webchat
    tool.raise_error_if_not_active()

    user_can_add = user_can_add_new_domain(request.user, conversation)
    host = get_host_with_schema(request)
    webchat_preview_url = host + conversation.patch_url("conversation-tools:webchat-preview")

    if "webchat-preview" in request.POST:
        RasaConversation.objects.get_or_create(conversation=conversation, domain=webchat_preview_url)
        return redirect(conversation.patch_url("conversation-tools:webchat-preview"))

    if request.method == "POST":
        form = RasaConversationForm(request.POST)
        if not user_can_add:
            raise PermissionError("user is not allowed to create conversation rasa connections")
        if form.is_valid():
            form.save()
            form = RasaConversationForm()
    else:
        form = RasaConversationForm()

    conversation_rasa_connections = RasaConversation.objects.filter(conversation=conversation)
    context = {
        "conversation": conversation,
        "conversation_rasa_connections": conversation_rasa_connections,
        "tool": tool,
        "form": form,
        "is_valid_user": user_can_add,
        "webchat_preview_url": webchat_preview_url,
    }
    return render(request, "ej_tools/webchat.jinja2", context)


def webchat_preview(request, board_slug, conversation_id, slug):
    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Opinion Bots"), conversation).webchat
    tool.raise_error_if_not_active()

    host = get_host_with_schema(request)
    rasa_domain = WebchatHelper.get_rasa_domain(host)
    context = {"conversation": conversation, "rasa_domain": rasa_domain}
    return render(request, "ej_tools/webchat-preview.jinja2", context)


def delete_connection(request, board_slug, conversation_id, slug, connection_id):
    user = request.user

    rasa_connection = RasaConversation.objects.get(id=connection_id)
    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Opinion Bots"), conversation).webchat
    tool.raise_error_if_not_active()

    if user.is_staff or user.is_superuser or rasa_connection.conversation.author.id == user.id:
        rasa_connection.delete()
    elif rasa_connection.conversation.author.id != user.id:
        raise PermissionError("cannot delete conversation rasa connections from another user")
    else:
        raise PermissionError("user is not allowed to delete conversation rasa connections")

    return redirect(conversation.patch_url("conversation-tools:webchat"))


@can_access_tool_page
def mautic(request, board_slug, conversation_id, slug, oauth2_code=None):
    conversation = Conversation.objects.get(id=conversation_id)
    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Mautic"), conversation)
    tool.raise_error_if_not_active()

    error_message = None
    connections = None

    try:
        connections = ConversationMautic.objects.get(conversation=conversation)
        if oauth2_code:
            connections.code = oauth2_code
            connections.save()
    except Exception as e:
        print(e)

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
            conversation_mautic = ConversationMautic.objects.get(conversation_id=conversation.id)
            save_oauth2_tokens(https_ej_server, conversation_mautic, request.GET.get("code"))
        except Exception as e:
            conversation_mautic.delete()
            error_message = e.message

    context = {
        "conversation": conversation,
        "connections": connections,
        "tool": tool,
        "form": form,
        "errors": error_message,
    }
    return render(request, "ej_tools/mautic.jinja2", context)


@can_access_tool_page
def delete_mautic_connection(request, board_slug, conversation_id, slug, mautic_connection_id):
    conversation = Conversation.objects.get(id=conversation_id)
    mautic_connection = ConversationMautic.objects.get(conversation_id=conversation_id)

    user_signature = SignatureFactory.get_user_signature(conversation.author)
    tool = user_signature.get_tool(_("Mautic"), conversation)
    tool.raise_error_if_not_active()

    mautic_connection.delete()
    return redirect(conversation.patch_url("conversation-tools:mautic"))


def save_oauth2_tokens(ej_server_url, conversation_mautic, code):
    oauth2_service = MauticOauth2Service(ej_server_url, conversation_mautic)
    oauth2_service.save_tokens(code)
