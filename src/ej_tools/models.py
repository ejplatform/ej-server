import requests
import json
from django.utils.translation import ugettext_lazy as _
from boogie import models
from boogie.rest import rest_api
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from requests import Request

from .constants import MAX_CONVERSATION_DOMAINS
from .utils import prepare_host_with_https


@rest_api(["conversation", "domain"])
class RasaConversation(models.Model):
    """
    Allows correlation between a conversation and an instance of rasa
    running on an external website
    """

    conversation = models.ForeignKey(
        "ej_conversations.Conversation", on_delete=models.CASCADE, related_name="rasa_conversations"
    )

    domain = models.URLField(
        _("Domain"),
        max_length=255,
        help_text=_("The domain that the rasa bot webchat is hosted."),
    )

    class Meta:
        unique_together = (("conversation", "domain"),)
        ordering = ["-id"]

    @property
    def reached_max_number_of_domains(self):
        try:
            num_domains = RasaConversation.objects.filter(conversation=self.conversation).count()
            return num_domains >= MAX_CONVERSATION_DOMAINS
        except Exception as e:
            return False

    def clean(self):
        super().clean()
        if self.reached_max_number_of_domains:
            raise ValidationError(_("a conversation can have a maximum of five domains"))


class ConversationComponent:
    """
    ConversationComponent controls the steps to generate the script and css to
    configure the EJ opinion web component;
    """

    AUTH_TYPE_CHOICES = (
        ("register", _("Register using name/email")),
        ("mautic", _("Mautic")),
        ("analytics", _("Analytics")),
    )

    AUTH_TOOLTIP_TEXTS = {
        "register": _("User will use EJ platform interface, creating an account using personal data"),
        "mautic": _("Uses a mautic campaign "),
        "analytics": _("Uses analytics cookies allowing you to cross vote data with user browser data."),
    }

    THEME_CHOICES = (
        ("default", _("Default")),
        ("votorantim", _("Votorantim")),
        ("icd", _("ICD")),
    )

    THEME_PALETTES = {
        "default": ["#1D1088", "#F8127E"],
        "votorantim": ["#04082D", "#F14236"],
        "icd": ["#005BAA", "#F5821F"],
    }

    def __init__(self, form):
        self.form = form

    def _form_is_invalid(self):
        return not self.form.is_valid() or (
            not self.form.cleaned_data["theme"] and not self.form.cleaned_data["authentication_type"]
        )

    def get_props(self):
        if self._form_is_invalid():
            return "theme= authenticate-with=register"

        result = ""
        if self.form.cleaned_data["theme"] != "default":
            result = result + f"theme={self.form.cleaned_data['theme']}"
        if self.form.cleaned_data["authentication_type"]:
            result = result + f" authenticate-with={self.form.cleaned_data['authentication_type']}"
        return result


class MailingTool:
    MAILING_TOOL_CHOICES = (
        ("mautic", _("Mautic")),
        ("mailchimp", _("MailChimp")),
    )

    MAILING_TOOLTIP_TEXTS = {
        "mailchimp": _("Mailchimp campaign"),
        "mautic": _("Uses a mautic campaign "),
    }


class ConversationMautic(models.Model):
    """
    Allows correlation between a conversation and an instance of Mautic
    """

    client_id = models.CharField(_("Client ID"), max_length=100)
    client_secret = models.CharField(_("Client Secret"), max_length=200)
    access_token = models.CharField(_("Mautic Access Token"), max_length=200, blank=True)
    refresh_token = models.CharField(_("Refresh Token"), max_length=200, blank=True)
    url = models.URLField(_("Mautic URL"), max_length=255, help_text=_("Generated Url from Mautic."))
    conversation = models.ForeignKey(
        "ej_conversations.Conversation", on_delete=models.CASCADE, related_name="mautic_integration"
    )

    class Meta:
        unique_together = (("conversation", "url"),)
        ordering = ["-id"]

    def has_oauth2_tokens(self):
        return self.access_token and self.refresh_token

    def oauth2_attributes_are_valid(self):
        return self.url and self.client_id and self.client_secret

    def save_oauth2_tokens(self, oauth2_access_token, oauth2_refresh_token=None):
        self.access_token = oauth2_access_token
        self.refresh_token = oauth2_refresh_token or self.refresh_token
        self.save()


class MauticOauth2Service:
    """
    Authentication flow on Mautic instance, from EJ data form on tools Mautic page.
    """

    NOT_FOUND_CODE = 404
    TIMEOUT_CODE = 504
    BAD_REQUEST_CODE = 400

    def __init__(self, ej_server_url, conversation_mautic):
        self.conversation_mautic = conversation_mautic
        self.redirect_uri = ej_server_url + self.conversation_mautic.conversation.url(
            "conversation-tools:mautic"
        )
        self.oauth2_authorization_url = self.conversation_mautic.url + "/oauth/v2/authorize"
        self.oauth2_token_url = self.conversation_mautic.url + "/oauth/v2/token"

    def build_body_params(self, complementary_params={}, grant_type="authorization_code"):
        default_params = {
            "client_id": self.conversation_mautic.client_id,
            "redirect_uri": self.redirect_uri,
            "grant_type": grant_type,
        }
        default_params.update(complementary_params)
        return default_params

    def generate_oauth2_url(self):
        """
        Prepare URL with code to get all tokens necessary to access Mautic API.
        """

        params = self.build_body_params({"response_type": "code"})
        oauth2_url = self.oauth2_authorization_url
        oauth2_url_with_params = Request("GET", oauth2_url, params=params).prepare().url
        if self.is_mautic_available(oauth2_url, params):
            return oauth2_url_with_params

    def is_mautic_available(self, oauth2_url, params):
        """
        Since the mautic endpoint /authorize redirect always return 200 code,
        that GET request is only useful here to check if the mautic is available.
        """

        mautic_response = requests.get(oauth2_url, json=params)

        if mautic_response.status_code == MauticOauth2Service.NOT_FOUND_CODE:
            raise ValidationError(_("Client not found."))
        elif mautic_response.status_code == MauticOauth2Service.TIMEOUT_CODE:
            raise ValidationError(
                _(
                    "Couldn't find a mautic instance on the url provided. Check your mautic url inserted here and the redirect url registered on Mautic page."
                )
            )
        return True

    def save_tokens(self, code):
        """
        Post request to generate access and refresh token.
        """

        if not self.conversation_mautic.has_oauth2_tokens():
            complementary_params = {
                "client_secret": self.conversation_mautic.client_secret,
                "code": code,
            }
            params = self.build_body_params(complementary_params)

            try:
                response = requests.post(self.oauth2_token_url, json=params)
                result = json.loads(response.text)
            except:
                raise ValidationError(_("Couldn't generate tokens."))
            self.conversation_mautic.save_oauth2_tokens(result["access_token"], result["refresh_token"])
        else:
            return None

    def generate_new_token(self):
        """
        Request to generate new token in case the access token is expired.
        The time expiration can be configured on Mautic instance interface.
        Time default is 3600s (1 hour).
        """

        complementary_params = {
            "client_secret": self.conversation_mautic.client_secret,
            "refresh_token": self.conversation_mautic.refresh_token,
        }
        params = self.build_body_params(complementary_params, "refresh_token")
        try:
            response = requests.post(self.oauth2_token_url, json=params)
            result = json.loads(response.text)
            self.conversation_mautic.save_oauth2_tokens(result["access_token"])
            return response
        except:
            raise ValidationError(_("Couldn't generate new token."))


class MauticClient:

    CONTACT_SEARCH_COMMAND = "?where%5B0%5D%5Bcol%5D=phone&where%5B0%5D%5Bexpr%5D=eq&where%5B0%5D%5Bval%5D="
    API_CONTACT_ENDPOINT = "/api/contacts"

    def __init__(self, conversation_mautic):
        self.conversation_mautic = conversation_mautic
        self.create_contact_url = conversation_mautic.url + MauticClient.API_CONTACT_ENDPOINT + "/new"

    def api_headers_with_authorization(self):
        default_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {self.conversation_mautic.access_token}",
        }
        return default_headers

    def get_contacts_url(self, phone_number):
        get_contacts_url = (
            self.conversation_mautic.url
            + MauticClient.API_CONTACT_ENDPOINT
            + MauticClient.CONTACT_SEARCH_COMMAND
            + phone_number
        )
        return get_contacts_url

    def check_existent_contact(self, ej_server_url, phone_number):
        """
        get contacts with that phone number, returning a total of them and their details
        https://developer.mautic.org/?json#list-contacts

        """

        if (
            self.conversation_mautic.oauth2_attributes_are_valid()
            and self.conversation_mautic.has_oauth2_tokens()
        ):
            try:
                response = requests.get(
                    self.get_contacts_url(phone_number),
                    headers=self.api_headers_with_authorization(),
                )
            except Exception as e:
                raise ValidationError(
                    _("There was an error connection to mautic server, please check your url.")
                )

            if response.status_code == 401:
                response = self.renew_oauth2_token(ej_server_url, phone_number)

            return MauticClient.contact_exists_on_mautic(response)

    @staticmethod
    def contact_exists_on_mautic(response):
        response_content = json.loads(response.text)
        if int(response_content["total"]) > 0:
            return True

    def renew_oauth2_token(self, ej_server_url, phone_number):
        """
        In case response code is 401 in the first contact with API,
        it means access token is expired. It should then generate a new token.
        After that, a new atempt of contact with API is made.
        """

        oauth2_service = MauticOauth2Service(ej_server_url, self.conversation_mautic)
        response = oauth2_service.generate_new_token()
        response = requests.get(
            self.get_contacts_url(phone_number),
            headers=self.api_headers_with_authorization(),
        )
        return response

    def check_or_create_contact(self, phone_number, ej_server_url):
        params = {"phone": phone_number}
        if not self.check_existent_contact(ej_server_url, phone_number):
            try:
                create_new_contact = requests.post(
                    self.create_contact_url,
                    data=params,
                    headers=self.api_headers_with_authorization(),
                )
            except Exception as e:
                raise ValidationError(_("Couldn't create a new contact in Mautic."))

            if not create_new_contact.status_code == 201:
                raise ValidationError(
                    _("There was an error connection to mautic server, please try again.")
                )
            return create_new_contact

    def create_contact(self, request, vote):
        """
        After any given vote on tools, like Telegram or whatsapp, it should be created a contact on Mautic instance.
        The user must fill a phone number.
        This functions is called on src/ej_conversations/api.py on save_vote()
        """

        phone_number = request.user.profile.phone_number
        conversation = vote.comment.conversation
        conversation_mautic = ConversationMautic.objects.get(conversation=conversation)

        if phone_number != None and conversation_mautic:
            try:
                https_ej_server = prepare_host_with_https(request)
                self.check_or_create_contact(phone_number, https_ej_server)
                print("Voto relacionado a um contato no Mautic")
            except:
                pass

    @staticmethod
    def redirect_to_mautic_oauth2(ej_server_url, conversation_mautic):
        oauth2_service = MauticOauth2Service(ej_server_url, conversation_mautic)
        oauth2_url = oauth2_service.generate_oauth2_url()
        return redirect(oauth2_url)
