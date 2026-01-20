from fastapi import HTTPException


class InvalidCredentials(HTTPException):
    """
    Username or password is incorrect
    """

    def __init__(self) -> None:
        """
        Initialize invalid credentials error
        """
        status_code = 401
        detail = 'Invalid username or password. Dummy'

        super().__init__(
            status_code=status_code,
            detail=detail
        )


class Unauthorized(HTTPException):
    """
    Access is forbidden for the current user.
    """

    def __init__(self) -> None:
        """
        Initialize unauthorized error.

        :return: None
        """
        status_code = 403
        detail = "Access denied."

        super().__init__(
            status_code=status_code,
            detail=detail
        )
