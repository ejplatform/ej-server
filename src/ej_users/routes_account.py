import logging

from allauth.account import views as allauth
from boogie.router import Router
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from . import forms
from . import models

User = get_user_model()

app_name = 'ej_users'
urlpatterns = Router(
    template='account/{name}.jinja2',
    login=True,
)
log = logging.getLogger('ej')


#
# Account management
#
@urlpatterns.route('')
def index(request):
    return {
        'user': request.user,
        'profile': getattr(request.user, 'profile', None),
    }


@urlpatterns.route('logout/')
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return {'has_logout': True}
    return {'has_logout': False}


@urlpatterns.route('remove/')
def remove_account(request):
    form = forms.RemoveAccountForm(request=request)
    farewell_message = None
    if form.is_valid_post():
        user = request.user
        if form.cleaned_data['confirm'] is False:
            form.add_error('confirm', _('You must confirm that you want to remove your account.'))
        elif form.cleaned_data['email'] != user.email:
            form.add_error('email', _('Wrong e-mail address'))
        elif user.is_superuser:
            form.add_error(None, _('Cannot remove superuser accounts'))
        else:
            models.remove_account(user)
            farewell_message = _('We are sorry to see you go :(<br><br>Good luck in your journey.')
            log.info(f'User {request.user} removed their EJ account.')
    return {'form': form, 'farewell_message': farewell_message}


#
# Reuse allauth views
#
change_email = urlpatterns.register(
    allauth.EmailView.as_view(
        success_url=reverse_lazy('account:manage-email'),
    ),
    path='manage-email/',
    name='manage-email',
)

change_password = urlpatterns.register(
    allauth.PasswordChangeView.as_view(
        success_url=reverse_lazy('account:change-password'),
    ),
    path='change-password/',
    name='change-password',
)
