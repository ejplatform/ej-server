import json
import random
import string
from json import JSONDecodeError
from logging import getLogger
from pprint import pprint

import requests
from django.conf import settings
from sidekick import lazy, delegate_to, record

from .exceptions import ApiError

log = getLogger("ej")
DEBUG = settings.DEBUG


class RCConfigWrapper:
    url = delegate_to("config")
    api_url = property(lambda self: self.config.api_url or self.config.url)
    _config = None

    def __init__(self, config=None):
        if config is not None:
            self._config = config

    @lazy
    def config(self):
        return self._config or self.configs.default_config()

    @lazy
    def accounts(self):
        from .models import RCAccount

        return RCAccount.objects

    @lazy
    def configs(self):
        from .models import RCConfig

        return RCConfig.objects

    @property
    def has_config(self):
        return self.configs.default_config(raises=False) is not None

    def clean_config(self):
        del self.config
        return self

    admin_username = delegate_to("config")
    admin_password = delegate_to("config")
    admin_id = delegate_to("config")
    admin_token = delegate_to("config")

    def register(self, user, username):
        """
        Call Rocket.Chat API to register a new user, if not already registered.
        """
        password = random_password(30)
        email = user.email
        result = self.api_call(
            "users.create",
            auth="admin",
            raises=False,
            payload={"email": email, "name": user.name, "username": username, "password": password},
        )

        if not result.get("success"):
            error = result.get("error", result)
            log.warning(f"[rocket.register] Could not create Rocket.Chat user: {error}")
            raise ApiError(result)

        # Account created successfully in Rocket.Chat, create a replica in
        # Django
        return self.accounts.create(
            config=self.config,
            user=user,
            username=username,
            password=password,
            user_rc_id=result["user"]["_id"],
            user_rc_email=email,
            is_active=True,
            account_data=result,
        )

    def admin_login(self):
        response = self.password_login(self.admin_username, self.admin_password)
        config = self.config
        config.admin_token = response["data"]["authToken"]
        config.save()
        return response

    def login(self, user):
        """
        Force Django user to login at Rocket.Chat.

        User must already been registered with an RC username.
        """
        # Super-user share the global config account. Login will force login and
        # update the global config
        if user.is_superuser:
            self.admin_login()
            return record(
                config=self.config,
                username=self.admin_username,
                password=self.admin_password,
                auth_token=self.config.admin_token,
                user_rc_id=self.admin_id,
                user=user,
            )

        # Handle regular accounts
        account = self.accounts.get(user=user)
        if not account.is_active:
            raise PermissionError("cannot login with inactive accounts")

        response = self.password_login(account.username, account.password)
        account.auth_token = response["data"]["authToken"]
        account.save()
        return account

    def password_login(self, username, password):
        """
        Login with explicit credentials.
        """
        payload = {"username": username, "password": password}
        try:
            response = self.api_call("login", payload=payload)
        except ApiError as exc:
            if exc.is_permission_error:
                raise PermissionError("invalid credentials")
            raise
        log.info(f"[rocket] {username} successfully logged in at Rocket.Chat")
        return response

    def logout(self, user):
        """
        Force logout of RC user.
        """
        users = list(self.accounts.filter(user=user))
        if user.is_superuser:
            self.api_call("logout", auth="admin", method="post")
            self.config.admin_token = ""
            self.config.save()
        if not users:
            return

        account = users[0]
        user_id, auth_token = account.user_rc_id, account.auth_token
        if auth_token:
            auth = {"user_id": user_id, "auth_token": auth_token}
            self.api_call("logout", auth=auth, method="post")
            account.auth_token = ""
            account.save()
            log.info(f"{user} successfully logged out from Rocket.Chat")

    def get_auth_token(self, user):
        """
        Return the login auth token for the given user.
        """
        if user.is_superuser:
            token = self.admin_token
            if token:
                return token
            return self.renew_admin_token()
        else:
            token = self.accounts.get(user=user).auth_token
            if token:
                return token
            return self.renew_auth_token(user)

    def renew_admin_token(self):
        """
        Renew the admin user auth-token.
        """
        self.admin_login()
        return self.config.admin_token

    def renew_auth_token(self, user):
        """
        Log in with user again and renew its authentication token.
        """
        if not user.is_superuser:
            return self.login(user).auth_token
        raise PermissionError("cannot renew admin token. Please call renew_admin_token()")

    def api_call(
        self,
        uri,
        payload=None,
        query_args=None,
        headers=None,
        raises=True,
        method="post",
        auth=None,
        version="v1",
    ) -> dict:
        """
        Makes a call to Rocketchat API.

        Args:
            uri:
                Used to construct Rocket.Chat url as <rocketchat>/api/<version>/<uri>
            payload (JSON):
                JSON payload for the request
            query_args (dict):
                Query dictionary appended to the url.
            headers (dict):
                An optional dictionary of HTTP headers.
            raises (bool):
                If True (default) raises an ApiError for bad responses from the
                API, otherwise, return the response dictionary.
            method ('post', 'get'):
                HTTP method used on the request.
            auth:
                Either None, a user with a registered Rocket.Chat account or
                the string 'admin' for admin access to the API.
            version:
                Version of Rocket.Chat API (only v1 is valid for now)
        """
        url = normalize_api_url(self.api_url, version, uri, query_args)
        headers = normalize_headers(headers, auth, self)
        kwargs = {}

        # Payload
        if payload is not None and method == "post":
            kwargs["data"] = json.dumps(payload)
            headers["Content-Type"] = "application/json"
        method = getattr(requests, method)

        # Makes API request
        try:
            response = method(url, headers=headers, **kwargs)
            result = json.loads(response.content, encoding="utf-8")
            result["code"] = response.status_code
            result.setdefault("error", response.status_code != 200)
        except (requests.ConnectionError, JSONDecodeError) as exc:
            result = {"code": None, "message": str(exc), "error": type(exc).__name__, "status": "error"}

        if DEBUG:
            print("[ROCKET] API CALL TO", url)
            print("    auth:", auth)
            print("    headers:", headers)
            print("    payload:", payload)
            pprint(result)

        # If admin auth token expires, some requests made using the admin role
        # will fail with unpredicted messages. We must try again
        if result["error"] and auth == "admin":
            headers["X-Auth-Token"] = self.admin_login()["data"]["authToken"]
            return self.api_call(
                uri, payload, query_args=query_args, headers=headers, version=version, raises=raises
            )

        if raises and result["error"] is not False:
            raise ApiError(result)
        return result


def normalize_api_url(base, version, uri, args=None):
    if "://" not in base:
        base = "http://" + base

    query = ""
    if args:
        query_param = "&".join(f"{k}={v}" for k, v in args.items())
        query = f"?{query_param}"

    return f"{base}/api/{version}/{uri}{query}"


def normalize_headers(headers, auth, config):
    headers = dict(headers or {})
    if auth:
        if auth == "admin":
            id, token = config.admin_id, config.admin_token
        elif isinstance(auth, dict):
            id, token = auth["user_id"], auth["auth_token"]
        else:
            id, token = config.user_info(auth)
        headers.update({"X-Auth-Token": token, "X-User-Id": id})
    return headers


def random_password(size):
    return "".join(random.choice(string.ascii_letters) for _ in range(size))


def new_config():
    return RCConfigWrapper()
