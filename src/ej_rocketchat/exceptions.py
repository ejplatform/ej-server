class ApiError(Exception):
    """
    Raised for generic API errors.
    """

    value = property(lambda self: self.args[0])
    response = property(lambda self: self.value.get('response', {}))
    code = property(lambda self: self.value.get('code'))


class UserLoggedInError(Exception):
    """
    Raised when trying to force login for an already logged-in user.
    """

    value = ApiError.value
