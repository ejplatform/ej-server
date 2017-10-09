from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import MethodNotAllowed
from .models import Conversation, Comment, Vote
from .serializers import AuthorSerializer, ConversationSerializer
from .serializers import CommentSerializer, VoteSerializer


def list_conversations(request):
    """
    List all conversations.
    """
    if request.method == 'GET':
        conversations = Conversation.objects.all()
        serializer = ConversationSerializer(conversations, many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        raise MethodNotAllowed

@csrf_exempt
def create_conversation(request):
    """
    Create a new conversation.
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ConversationSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)
    else:
        raise MethodNotAllowed

def conversation_detail(request, pk):
    """
    Retrieve a conversation.
    """
    conversation = get_object_or_404(Conversation, pk=pk)

    if request.method == 'GET':
        serializer = ConversationSerializer(conversation)
        return JsonResponse(serializer.data)
    else:
        raise MethodNotAllowed

@csrf_exempt
def update_conversation(request, pk):
    """
    Edit a conversation
    """
    conversation = get_object_or_404(Conversation, pk=pk)

    if request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ConversationSerializer(conversation, data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        else:
            return JsonResponse(serializer.errors, status=400)
    else:
        raise MethodNotAllowed

@csrf_exempt
def delete_conversation(request, pk):
    """
    Remove a conversation
    """

    conversation = get_object_or_404(Conversation, pk=pk)

    if request.method == 'DELETE':
        conversation.delete()
        return HttpResponse(status=204)
    else:
        raise MethodNotAllowed
