from fastapi import HTTPException


class InvalidCredentials(HTTPException):
    """
    Username or password is incorrect
    """
    status_code = 401
    detail = "Invalid username or password."

    def __init__(self) -> None:
        """
        Initialize invalid credentials error
        """
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class Unauthorized(HTTPException):
    """
    Access is forbidden for the current user.
    """
    status_code = 403
    detail = "Access denied."

    def __init__(self) -> None:
        """
        Initialize unauthorized error.

        :return: None
        """
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )
