class ApiError(Exception):
    """
    Raised for generic API errors.
    """


class UserLoggedInError(Exception):
    """
    Raised when trying to force login for an already logged-in user.
    """
