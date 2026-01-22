from fastapi import HTTPException


class UserAlreadyExists(HTTPException):
    def __init__(self, username: str) -> None:
        status_code = 409
        detail = f'User with username "{username}" already exists. Choose a different username.'

        super().__init__(status_code=status_code, detail=detail)
