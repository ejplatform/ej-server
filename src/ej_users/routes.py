import logging
from functools import lru_cache

from boogie.router import Router
from django.apps import apps
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.authtoken.models import Token
from sidekick import record

from . import forms
from . import models
from . import password_reset_token
from .socialbuttons import social_buttons

User = get_user_model()

app_name = "ej_users"
urlpatterns = Router(
    template="ej_users/{name}.jinja2",
    models={"token": models.PasswordResetToken},
    lookup_field={"token": "url"},
)
log = logging.getLogger("ej")


@urlpatterns.route("login/")
def login(request, redirect_to="/"):
    form = forms.LoginForm(request=request)
    error_msg = _("Invalid email or password")
    next_url = request.GET.get("next", redirect_to)
    fast = request.GET.get("fast", "false") == "true" or "fast" in request.GET

    if form.is_valid_post():
        data = form.cleaned_data
        email, password = data["email"], data["password"]

        try:
            user = User.objects.get_by_email(email)
            user = auth.authenticate(request, email=user.email, password=password)
            if user is None:
                raise User.DoesNotExist
            auth.login(request, user, backend=user.backend)
            log.info(f"user {user} ({email}) successfully authenticated")
        except User.DoesNotExist:
            form.add_error(None, error_msg)
            log.info(f"invalid login attempt: {email}")
        else:
            return redirect(next_url)

    elif fast and request.user.is_authenticated and next_url:
        return redirect(next_url)

    return {
        "user": request.user,
        "form": form,
        "next": next_url,
        "social_js": social_js_template().render(request=request),
        "social_buttons": social_buttons(request),
    }


@urlpatterns.route("register/")
def register(request):
    form = forms.RegistrationForm(request=request)
    next_url = request.GET.get("next", "/")

    if form.is_valid_post():
        data = form.cleaned_data
        name, email, password = data["name"], data["email"], data["password"]

        try:
            user = User.objects.create_user(email, password, name=name)
            log.info(f"user {user} ({email}) successfully created")
        except IntegrityError as ex:
            form.add_error(None, str(ex))
            log.info(f"invalid login attempt: {email}")
        else:
            user = auth.authenticate(request, email=user.email, password=password)
            auth.login(request, user)
            response = redirect(next_url)
            response.set_cookie("show_welcome_window", "true")

            return response

    return {
        "user": request.user,
        "form": form,
        "next": next_url,
        "social_js": social_js_template().render(request=request),
        "social_buttons": social_buttons(request),
    }


@urlpatterns.route("recover-password/")
def recover_password(request):
    next_url = request.GET.get("next", "/login/")
    form = forms.EmailForm(request=request)
    user = None
    success = False

    if form.is_valid_post():
        success = True
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get_by_email(email)
        except User.DoesNotExist:
            pass
        else:
            send_recover_password_email(request, user, email)

    return {"user": user, "form": form, "success": success, "next": next_url}


@urlpatterns.route("recover-password/<model:token>/")
def recover_password_token(request, token):
    next_url = request.GET.get("next", "/login/")
    user = token.user
    form = forms.PasswordForm(request=request)

    if form.is_valid_post() and not (token.is_expired or token.is_used):
        password = form.cleaned_data["password"]
        user.set_password(password)
        user.save()
        token.delete()
        return redirect(next_url)

    return {
        "user": user,
        "form": form,
        "next": next_url,
        "is_expired": token.is_expired,
    }


#
# Registration via API + jsCookies
#
@urlpatterns.route("login/api-key/")
def api_key(request):
    if request.user.id is None:
        raise Http404
    token = Token.objects.get_or_create(user=request.user)
    return JsonResponse({"key": token[0].key}, status=status.HTTP_200_OK)


#
# Auxiliary functions and templates
#
@lru_cache(1)
def social_js_template():
    if apps.is_installed("allauth.socialaccount"):
        return get_template("socialaccount/snippets/login_extra.html")
    else:
        return record(render=lambda *args, **kwargs: "")


def send_recover_password_email(request, user, email):
    token = password_reset_token(user)
    from_email = settings.DEFAULT_FROM_EMAIL
    path = reverse("auth:recover-password-token", kwargs={"token": token})
    template = get_template("ej_users/recover-password-message.jinja2")
    email_body = template.render({"url": raw_url(request, path)}, request=request)
    send_mail(
        subject=_("Please reset your password"),
        message=email_body,
        from_email=from_email,
        recipient_list=[email],
    )
    log.info(f"user {user} requested a password reset.")


def raw_url(request, path):
    if not path.startswith("/"):
        path = request.path.rstrip("/") + "/" + path
    return f"{request.scheme}://{request.get_host()}{path}"
