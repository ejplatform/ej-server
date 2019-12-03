class ApiError(Exception):
    """
    Raised for generic API errors.
    """

    value = property(lambda self: self.args[0])
    code = property(lambda self: self.value.get("code"))
    status = property(lambda self: self.value.get("status", "success"))

    @property
    def error_message(self):
        if self.is_error:
            return self.value.get("error") or self.value.get("message", "unknown error")
        return ""

    @property
    def is_error(self):
        return self.status == "error" or self.value["error"]

    @property
    def is_permission_error(self):
        """
        Rocket.Chat error messages had changed in the past.
        We try to see if the error field of Payload is "unauthorized" or
        if the string "unauthorized" is present anywhere in the message.
        """
        raise NotImplementedError

    @property
    def is_too_many_requests_error(self):
        return "[error-too-many-requests]" in self.error_message


class UserLoggedInError(Exception):
    """
    Raised when trying to force login for an already logged-in user.
    """

    value = ApiError.value
