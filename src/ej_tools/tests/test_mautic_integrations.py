from requests.api import request
from urllib3.exceptions import HTTPError
import pytest
from django.utils.translation import ugettext as _
from unittest.mock import patch, MagicMock, Mock
from django.core.exceptions import ValidationError

from ej_conversations.mommy_recipes import ConversationRecipes
from ej_tools.forms import MauticConversationForm
from ej_tools.models import ConversationMautic, MauticOauth2Service, MauticClient

ConversationRecipes.update_globals(globals())

TEST_DOMAIN = "https://domain.com.br"
SUCCESS_CODE = 200
CREATED_CODE = 201
UNATHORIZED_CODE = 401
TIMEOUT_CODE = 408
TEST_PHONE_NUMBER = "6133213030"


def mock_requests():
    return


def conversation_mautic_mock(conversation):
    return {
        "client_id": "1273897123872837",
        "url": TEST_DOMAIN,
        "conversation": conversation,
        "client_secret": "97837483294798",
    }


class MockRequests:
    def __init__(self, get_status_code, post_status_code, get_response='{"total": 0}', post_response=None):
        self.get_code = get_status_code
        self.post_code = post_status_code
        self.mock_requests = mock_requests
        self.get_response = get_response
        self.post_response = post_response
        mock_requests.get = self.get
        mock_requests.post = self.post

    def get(self, url, headers=None, json=None):
        return MagicMock(status_code=self.get_code, text=self.get_response)

    def post(self, url, data=None, headers=None, json=None):
        return MagicMock(status_code=self.post_code, text=self.post_response)


class TestMauticConversationForm(ConversationRecipes):
    def test_mautic_conversation_valid_form(self, db, mk_conversation):
        conversation = mk_conversation()
        form = MauticConversationForm(data=conversation_mautic_mock(conversation.id))
        assert form.is_valid()

    def test_mautic_conversation_invalid_url_form(self, db, mk_conversation):
        conversation = mk_conversation()
        form = MauticConversationForm({"url": "invalidurl"}, initial={"conversation": conversation})

        assert not form.is_valid()
        assert _("Enter a valid URL.") == form.errors["url"][0]

    def test_mautic_conversation_empty_fields(self, db, mk_conversation):
        conversation = mk_conversation()

        form = MauticConversationForm(
            data={
                "client_id": None,
                "url": None,
                "conversation": conversation.id,
                "client_secret": None,
            }
        )
        assert not form.is_valid()
        assert _("This field is required.") == form.errors["client_id"][0]
        assert _("This field is required.") == form.errors["client_secret"][0]
        assert _("This field is required.") == form.errors["url"][0]


class TestConversationMauticModel:
    @patch("ej_tools.models.requests", MockRequests(SUCCESS_CODE, CREATED_CODE, '{"total": 0}'))
    def test_create_new_valid_contact_on_mautic(self, db, mk_conversation):
        conversation = mk_conversation()
        conversation_mautic_attributes = conversation_mautic_mock(conversation)
        conversation_mautic = ConversationMautic(**conversation_mautic_attributes)
        conversation_mautic.save()
        mautic_client = MauticClient(conversation_mautic)
        response = mautic_client.check_or_create_contact(TEST_PHONE_NUMBER, TEST_DOMAIN)
        assert response.status_code == 201

    @patch("ej_tools.models.requests", MockRequests(SUCCESS_CODE, CREATED_CODE))
    def test_create_mautic_connection_with_valid_url(self, db, mk_conversation):
        conversation = mk_conversation()
        conversation_mautic_attributes = conversation_mautic_mock(conversation)
        conversation_mautic = ConversationMautic(**conversation_mautic_attributes)
        conversation_mautic.save()
        oauth2_service = MauticOauth2Service(TEST_DOMAIN, conversation_mautic)
        response = oauth2_service.generate_oauth2_url()
        assert TEST_DOMAIN in response

    @patch(
        "ej_tools.models.requests",
        MockRequests(MauticOauth2Service.TIMEOUT_CODE, CREATED_CODE),
    )
    def test_create_mautic_connection_with_invalid_url(self, db, mk_conversation):
        conversation = mk_conversation()
        conversation_mautic_attributes = conversation_mautic_mock(conversation)
        conversation_mautic = ConversationMautic(**conversation_mautic_attributes)
        conversation_mautic.save()
        oauth2_service = MauticOauth2Service(TEST_DOMAIN, conversation_mautic)
        with pytest.raises(ValidationError) as validationError:
            oauth2_service.generate_oauth2_url()
        assert (
            _(
                "Couldn't find a mautic instance on the url provided. Check your mautic url inserted here and the redirect url registered on Mautic page."
            )
            == validationError.value.message
        )

    @patch(
        "ej_tools.models.requests",
        MockRequests(
            CREATED_CODE,
            MauticOauth2Service.BAD_REQUEST_CODE,
            post_response='{"access_token": "something"}',
        ),
    )
    def test_generate_new_token_when_expired(self, db, mk_conversation):
        conversation = mk_conversation()
        conversation_mautic_attributes = conversation_mautic_mock(conversation)
        conversation_mautic = ConversationMautic(**conversation_mautic_attributes)
        conversation_mautic.save()
        oauth2_service = MauticOauth2Service(TEST_DOMAIN, conversation_mautic)
        response = oauth2_service.generate_new_token()
        assert response.status_code == MauticOauth2Service.BAD_REQUEST_CODE

    @patch("ej_tools.models.requests", MockRequests(TIMEOUT_CODE, SUCCESS_CODE))
    def test_create_mautic_connection_timeout(self, db, mk_conversation):
        conversation = mk_conversation()
        conversation_mautic_attributes = conversation_mautic_mock(conversation)
        conversation_mautic = ConversationMautic(**conversation_mautic_attributes)
        conversation_mautic.save()
        with pytest.raises(ValidationError) as validationError:
            mautic_client = MauticClient(conversation_mautic)
            mautic_client.check_or_create_contact(TEST_PHONE_NUMBER, TEST_DOMAIN)
        assert (
            _("There was an error connection to mautic server, please try again.")
            == validationError.value.message
        )
