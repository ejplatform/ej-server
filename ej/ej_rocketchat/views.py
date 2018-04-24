from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from constance import config

from .decorators import allow_credentials
from . import helpers

import sys


@csrf_exempt
@allow_credentials
@xframe_options_exempt
def check_login(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    name = (request.user.first_name + ' ' + request.user.last_name).strip()
    loginToken = helpers.create_user_token(
        request.user.email,
        name or request.user.username,
        request.user.username
    )

    return JsonResponse({'loginToken': loginToken })


def rc_redirect(request):
    return redirect(config.ROCKETCHAT_URL)
