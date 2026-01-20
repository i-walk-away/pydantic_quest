from src.app.core.auth_manager import AuthManager
from src.app.core.exceptions.auth_exc import InvalidCredentials
from src.app.domain.models.dto.auth import LoginCredentials
from src.app.domain.repositories import UserRepository


class AuthService:
    def __init__(
            self,
            user_repository: UserRepository,
            auth_manager: AuthManager
    ):
        self.user_repository = user_repository
        self.auth_manager = auth_manager

    async def login(self, credentials: LoginCredentials) -> str:
        """
        Authenticate given credentials

        :param credentials: login credentials
        :return: JSON Web Token
        """
        is_authenticated = await self._validate_credentials(credentials=credentials)

        if not is_authenticated:
            raise InvalidCredentials

        return self.auth_manager.generate_jwt(input_data={"sub": credentials.username})

    async def _validate_credentials(self, credentials: LoginCredentials) -> bool:
        """
        Check if given credentials are valid

        :param credentials: username and password
        :return: True if credentials are valid, otherwise False
        """
        user = await self.user_repository.get_by_username(username=credentials.username)

        is_password_correct = self.auth_manager.verify_password_against_hash(
            plain_password=credentials.plain_password,
            hashed_password=user.hashed_password
        )

        return is_password_correct
