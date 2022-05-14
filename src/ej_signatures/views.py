from django.shortcuts import render
from ej_signatures.services.slack import SlackService
from ej_boards.models import Board


def list_view(request, board_slug):
    user = request.user
    signature = user.signature

    context = {
        "signature": signature,
        "success": False,
        "user_boards": Board.objects.filter(owner=user),
        "board_slug": board_slug,
    }

    return render(request, "ej_signatures/signatures-list.jinja2", context)


def upgrade(request, board_slug):
    if request.method != "POST":
        return list_view(request, board_slug)

    user = request.user

    slack = SlackService()
    slack.notify_request(request)

    context = {
        "signature": user.signature,
        "success": True,
        "user_boards": Board.objects.filter(owner=user),
        "board_slug": board_slug,
    }

    return render(request, "ej_signatures/signatures-list.jinja2", context)
