from logging import getLogger

from boogie.router import Router
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from ej_users.forms import LoginForm
from ej_users.routes import social_js_template
from ej_users.socialbuttons import social_buttons
from . import forms
from .decorators import security_policy, requires_rc_perm
from .models import RCConfig, RCAccount, CAN_LOGIN_PERM
from .rocket import rocket

log = getLogger("ej")
app_name = "ej_rocketchat"
urlpatterns = Router(template=["ej_rocketchat/{name}.jinja2"])


@urlpatterns.route("", decorators=[security_policy])
def index(request):
    base_url = request.scheme + "://" + request.get_host()

    if not request.user.has_perm(CAN_LOGIN_PERM):
        return render(request, "ej_rocketchat/forbidden.jinja2")

    # Superuser must type the password since it is not stored in the database
    if not rocket.has_config:
        if request.user.is_superuser:
            cfg = RCConfig.objects.default_config(raises=False)
            form = forms.RocketIntegrationForm(request=request)
            form.fields["rocketchat_url"].initial = getattr(cfg, "url", "http://localhost:3000")

            if form.is_valid_post():
                password = form.cleaned_data["password"]
                username = form.cleaned_data["username"]
                rocket.password_login(username, password)
                return redirect(rocket.url)

            return render(request, "ej_rocketchat/config.jinja2", {"form": form})

        return render(request, "ej_rocketchat/forbidden.jinja2")

    elif request.user.is_superuser:
        return redirect(rocket.url)

    else:
        account = rocket.find_or_create_account(request.user)
        if account is None:
            return redirect("rocket:register")

    ctx = {"url": rocket.url + "/home/", "url_escape": repr(rocket.url + "/home/"), "base_url": base_url}
    return render(request, "ej_rocketchat/redirect.jinja2", ctx)


@urlpatterns.route("register/", decorators=[requires_rc_perm])
def register(request):
    if RCAccount.objects.filter(user=request.user).exists():
        return redirect("rocket:index")

    form = forms.CreateUsernameForm(request=request, user=request.user)
    if form.is_valid_post():
        return redirect("rocket:index")
    return {"form": form}


@urlpatterns.route("intro/", login=False, decorators=[security_policy])
def intro(request):
    base_url = request.scheme + "://" + request.get_host()
    return {"base_url": base_url}


@urlpatterns.route("login/", decorators=[security_policy])
def login(request):
    form = LoginForm(request=request)
    error_msg = _("Invalid email or password")
    auth_token = None

    if request.user.is_authenticated:
        auth_token = rocket.get_auth_token(request.user)

    if form.is_valid_post():
        data = form.cleaned_data
        email, password = data["email"], data["password"]
        user_model = get_user_model()

        try:
            user = user_model.objects.get_by_email(email)
            user = auth.authenticate(request, email=user.email, password=password)
            if user is None:
                raise user_model.DoesNotExist
            auth.login(request, user, backend=user.backend)
            log.info(f"user {user} ({email}) successfully authenticated")
        except user_model.DoesNotExist:
            form.add_error(None, error_msg)
            log.info(f"invalid login attempt: {email}")
        else:
            auth_token = rocket.get_auth_token(user)

    return {
        "user": request.user,
        "next": None,
        "auth_token": auth_token,
        "rocket_chat_url": rocket.url,
        "form": form,
        "social_js": social_js_template().render(request=request),
        "social_buttons": social_buttons(request),
    }


@urlpatterns.route("api-login/", decorators=[security_policy])
def api_login(request):
    try:
        if not request.user.is_authenticated:
            log.warning(f"Rocket.Chat: anonymous user login attempt.")
            return HttpResponse(status=401)

        auth_token = rocket.get_auth_token(request.user)
        log.info(f"Rocket.Chat: {request.user} attempted login")
        return JsonResponse({"loginToken": auth_token})
    except PermissionError:
        log.warning("Rocket.Chat: Login attempt by invalid RC user: {exc}")
        return HttpResponse(status=401)
    except Exception as exc:
        msg = "Rocket.Chat: Exception raised when user attempted an API rocket chat login, "
        msg += f"{exc.__name__.__class__}: {exc}"
        log.error(msg)
        return HttpResponse(status=401)
