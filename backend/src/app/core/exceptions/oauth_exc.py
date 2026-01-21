from fastapi import HTTPException


class OAuthConfigError(HTTPException):
    """
    OAuth configuration error.
    """
    status_code = 500
    detail = "OAuth configuration is incomplete."

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize OAuth config error.

        :param detail: error details

        :return: None
        """
        if detail:
            self.detail = detail
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class OAuthStateError(HTTPException):
    """
    OAuth state validation error.
    """
    status_code = 400
    detail = "OAuth state validation failed."

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize OAuth state error.

        :param detail: error details

        :return: None
        """
        if detail:
            self.detail = detail
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class OAuthTokenExchangeError(HTTPException):
    """
    OAuth token exchange error.
    """
    status_code = 400
    detail = "OAuth token exchange failed."

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize OAuth token exchange error.

        :param detail: error details

        :return: None
        """
        if detail:
            self.detail = detail
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class OAuthTokenMissingError(HTTPException):
    """
    OAuth token missing error.
    """
    status_code = 400
    detail = "OAuth access token is missing."

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize OAuth token missing error.

        :param detail: error details

        :return: None
        """
        if detail:
            self.detail = detail
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class OAuthUserFetchError(HTTPException):
    """
    OAuth user fetch error.
    """
    status_code = 400
    detail = "OAuth user fetch failed."

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize OAuth user fetch error.

        :param detail: error details

        :return: None
        """
        if detail:
            self.detail = detail
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class OAuthEmailFetchError(HTTPException):
    """
    OAuth email fetch error.
    """
    status_code = 400
    detail = "OAuth email fetch failed."

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize OAuth email fetch error.

        :param detail: error details

        :return: None
        """
        if detail:
            self.detail = detail
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class OAuthEmailNotVerifiedError(HTTPException):
    """
    OAuth email verification error.
    """
    status_code = 400
    detail = "OAuth account has no verified email."

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize OAuth email verification error.

        :param detail: error details

        :return: None
        """
        if detail:
            self.detail = detail
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )


class OAuthAccountConflict(HTTPException):
    """
    OAuth account conflicts with existing user.
    """
    status_code = 409
    detail = "OAuth account conflicts with existing user."

    def __init__(self, detail: str | None = None) -> None:
        """
        Initialize OAuth account conflict error.

        :param detail: error details

        :return: None
        """
        if detail:
            self.detail = detail
        super().__init__(
            status_code=self.status_code,
            detail=self.detail
        )
