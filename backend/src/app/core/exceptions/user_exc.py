from fastapi import HTTPException


class UserAlreadyExists(HTTPException):
    def __init__(self, username: str) -> None:
        status_code = 409
        detail = f'User with username "{username}" already exists. Choose a different username.'

        super().__init__(status_code=status_code, detail=detail)


class UserEmailAlreadyExists(HTTPException):
    def __init__(self, email: str) -> None:
        status_code = 409
        detail = f'User with email "{email}" already exists. Choose a different email.'

        super().__init__(status_code=status_code, detail=detail)


class UserPasswordChangeInvalid(HTTPException):
    def __init__(self, detail: str) -> None:
        status_code = 400
        super().__init__(status_code=status_code, detail=detail)
