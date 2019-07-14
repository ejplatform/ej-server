import random
import string
from logging import getLogger

from sidekick import lazy, delegate_to, record

from .exceptions import ApiError

log = getLogger("ej")


class RCConfigWrapper:
    @property
    def config(self):
        return self.configs.default_config()

    @property
    def url(self):
        return self.config.url

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
            log.warning(f"Could not create Rocket.Chat user: {error}")
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

    def login(self, user):
        """
        Force Django user to login at Rocket.Chat.

        User must already been registered and provided a RC username.
        """
        # Super-user share the global config account. Login will force login and
        # update the global config
        if user.is_superuser:
            from .models import RCAccount

            response = self.password_login(self.admin_username, self.admin_password)
            self.config.admin_token = response["data"]["authToken"]
            self.config.save()
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
            return account

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
        log.info(f"{username} successfully logged in at Rocket.Chat")
        return response

    def logout(self, user):
        """
        Force logout of RC user.
        """
        users = list(self.accounts.filter(user=user))
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

    def get_auth_token(self, user, fast=False):
        """
        Return the login auth token for the given user.
        """
        if fast and user.is_superuser:
            return self.admin_token
        elif fast:
            return self.accounts.get(user=user).auth_token

        account = self.login(user)
        return account.auth_token

    def api_call(self, *args, **kwargs):
        """
        Calls Rocket.Chat API and return the response.

        Raise ApiError if response code is not 200.
        """
        return self.config.api_call(*args, **kwargs)

    def api_user_update(self, id, **kwargs):
        """
        Update user with parameters.

        Example:
            >>> rocket.api_user_update(user_id, password='pass1234word')
        """
        payload = {"userId": id, "data": kwargs}
        result = self.api_call(f"users.update", payload=payload, auth="admin")
        return result["user"]

    def find_or_create_account(self, user):
        """
        Tries to find and create a rocket user account for the given user.

        This method does not check if user has permission and can create a
        RC account even for a user that does not have the proper permission.

        Return None if no account is found.
        """
        try:
            return self.accounts.get(user=user)
        except self.accounts.model.DoesNotExist:
            pass
        return None


rocket = RCConfigWrapper()


def random_password(size):
    return "".join(random.choice(string.ascii_letters) for _ in range(size))
