from src.app.core.exceptions.auth_exc import InvalidCredentials
from src.app.core.security.auth_manager import AuthManager
from src.app.domain.models.db.user import User
from src.app.domain.models.dto.auth import LoginCredentials
from src.app.domain.repositories import UserRepository


class AuthService:
    def __init__(
            self,
            user_repository: UserRepository,
            auth_manager: AuthManager,
    ) -> None:
        self.user_repository = user_repository
        self.auth_manager = auth_manager

    async def login(self, credentials: LoginCredentials) -> str:
        """
        Authenticate given credentials

        :param credentials: login credentials
        :return: JSON Web Token
        """
        user = await self._get_authenticated_user(credentials=credentials)

        if not user:
            raise InvalidCredentials

        return self.auth_manager.generate_jwt(
            input_data={
                "sub": user.username,
                "role": user.role.value,
            },
        )

    async def _get_authenticated_user(self, credentials: LoginCredentials) -> User | None:
        """
        Check if given credentials are valid

        :param credentials: username and password
        :return: user if credentials are valid, otherwise None
        """
        user = await self.user_repository.get_by_username(username=credentials.username)

        if not user:
            return None

        hashed_password = user.hashed_password

        if hashed_password is None:
            return None

        is_password_correct = self.auth_manager.verify_password_against_hash(
            plain_password=credentials.plain_password,
            hashed_password=hashed_password,
        )

        if not is_password_correct:
            return None

        return user
