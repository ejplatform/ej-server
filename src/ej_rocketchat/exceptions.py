class ApiError(Exception):
    """
    Raised for generic API errors.
    """

    response = property(lambda self: self.value.get("response", {}))
    code = property(lambda self: self.value.get("code"))

    @property
    def value(self):
        value = self.args[0]
        return value if isinstance(value, dict) else {'value': value}

    @property
    def is_permission_error(self):
        # Rocket.Chat error messages had changed in the past.
        # We try to see if the error field of Payload is "unauthorized" or
        # if the string "unauthorized" is present anywhere in the message.
        return (str(self.response.get("error", '')).lower() == "unauthorized"
                or "unauthorized" in str(self.response).lower())


class UserLoggedInError(Exception):
    """
    Raised when trying to force login for an already logged-in user.
    """

    value = ApiError.value
