from django.shortcuts import redirect
from ej_conversations.models.conversation import Conversation


def can_edit_conversation(view_func):
    def wrapper_func(request, *args, **kwargs):
        try:
            conversation_id = kwargs.get("conversation_id")
            conversation = Conversation.objects.get(id=conversation_id)
        except AttributeError:
            return redirect("auth:login")

        if request.user.id == conversation.author_id:
            return view_func(request, *args, **kwargs)
        elif conversation.is_promoted and request.user.has_perm("ej_conversations.can_publish_promoted"):
            return view_func(request, *args, **kwargs)
        return redirect("auth:login")

    return wrapper_func


def can_access_tool_page(view_func):
    """
    Can access a tool page from a conversation.

    * User is staff
    * OR user is an superuser
    * OR user is the conversation author
    """

    def wrapper_func(request, *args, **kwargs):
        try:
            conversation_id = kwargs.get("conversation_id")
            conversation = Conversation.objects.get(id=conversation_id)
        except AttributeError:
            return redirect("auth:login")
        if request.user.is_staff or request.user.is_superuser or conversation.author.id == request.user.id:
            return view_func(request, *args, **kwargs)
        return redirect("auth:login")

    return wrapper_func
