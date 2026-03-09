from uuid import UUID

from src.app.core.exceptions.auth_exc import InvalidCredentials
from src.app.core.exceptions.base_exc import NotFoundError
from src.app.core.exceptions.user_exc import (
    UserAlreadyExists,
    UserEmailAlreadyExists,
)
from src.app.core.security.auth_manager import AuthManager
from src.app.domain.models.db.user import User
from src.app.domain.models.dto.user import CreateUserDTO, UpdateUserDTO, UserDTO
from src.app.domain.repositories import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository, auth_manager: AuthManager) -> None:
        """
        Initialize user service.

        :param user_repository: user repository

        :return: None
        """
        self.repository = user_repository
        self.auth_manager = auth_manager

    async def get_by_id(self, id: UUID) -> UserDTO:
        """
        Get user by id.

        :param id: user id

        :return: user dto
        """
        user = await self._require_user(id=id)

        return user.to_dto()

    async def get_by_username(self, username: str) -> UserDTO:
        """
        Gets user by username from the database.

        :param username: user's username
        :return: UserDTO representing a user.
        """
        user = await self.repository.get_by_username(username=username)

        if not user:
            raise NotFoundError(
                entity_type_str='User',
                field_name='username',
                field_value=username,
            )

        return user.to_dto()

    async def get_all(self) -> list[UserDTO]:
        """
        Get all users.

        :return: user list
        """
        users = await self.repository.get_all()

        return [user.to_dto() for user in users]

    async def create(self, schema: CreateUserDTO) -> UserDTO:
        """
        Create new user.

        :param schema: DTO object containing fields needed to construct new User

        :return: DTO representation of created User
        """
        await self._validate_username_available(username=schema.username)

        hashed_password = self.auth_manager.hash_password(password=schema.plain_password)
        data = schema.model_dump()

        user = User(
            **data,
            hashed_password=hashed_password,
        )

        await self.repository.add(model=user)
        await self.repository.session.commit()
        await self.repository.session.refresh(instance=user)

        return user.to_dto()

    async def delete(self, id: UUID) -> bool:
        """
        Delete user from the database.

        :param id: user id

        :return: True if user was deleted
        """
        _ = await self._require_user(id=id)

        deleted = await self.repository.delete(id=id)

        if not deleted:
            raise NotFoundError(
                entity_type_str='User',
                field_name='id',
                field_value=id,
            )

        await self.repository.session.commit()

        return deleted

    async def update_me(self, id: UUID, schema: UpdateUserDTO) -> UserDTO:
        """
        Update current user data.

        :param id: user id
        :param schema: update data

        :return: updated user dto
        """
        user = await self._require_user(id=id)
        data = await self._build_update_data(
            user=user,
            schema=schema,
        )

        if not data:
            return user.to_dto()

        updated = await self.repository.update(
            id=id,
            data=data,
        )

        if updated is None:
            raise NotFoundError(
                entity_type_str='User',
                field_name='id',
                field_value=id,
            )

        await self.repository.session.commit()
        await self.repository.session.refresh(instance=updated)

        return updated.to_dto()

    async def _validate_username_available(self, username: str) -> None:
        """
        Validate username uniqueness before creating a user.

        The helper keeps create flow deterministic and produces a clear domain
        conflict error before hitting database constraints.

        :param username: requested username

        :return: None
        """
        user = await self.repository.get_by_username(username=username)

        if user is not None:
            raise UserAlreadyExists(username=user.username)

    async def _require_user(self, id: UUID) -> User:
        """
        Resolve user by id or raise not found error.

        This helper keeps public service methods focused on business actions
        while preserving one consistent not-found contract.

        :param id: user id

        :return: user model
        """
        user = await self.repository.get(id=id)

        if user is None:
            raise NotFoundError(
                entity_type_str='User',
                field_name='id',
                field_value=id,
            )

        return user

    async def _build_update_data(self, user: User, schema: UpdateUserDTO) -> dict[str, object]:
        """
        Build update payload for current user profile changes.

        This helper centralizes uniqueness checks and password transition rules
        so update_me remains a thin orchestration method.

        :param user: current user model
        :param schema: requested user updates

        :return: repository update payload
        """
        data = schema.model_dump(exclude_unset=True, exclude_none=True)
        await self._validate_username_change(
            user=user,
            new_username=data.get("username"),
        )
        await self._validate_email_change(
            user=user,
            new_email=data.get("email"),
        )
        self._enrich_password_change(
            user=user,
            schema=schema,
            data=data,
        )

        return data

    async def _validate_username_change(self, user: User, new_username: object | None) -> None:
        """
        Validate username change request.

        :param user: current user model
        :param new_username: requested username value

        :return: None
        """

        if not isinstance(new_username, str):
            return

        if new_username == user.username:
            return

        existing = await self.repository.get_by_username(username=new_username)

        if existing is not None and existing.id != user.id:
            raise UserAlreadyExists(username=new_username)

    async def _validate_email_change(self, user: User, new_email: object | None) -> None:
        """
        Validate email change request.

        :param user: current user model
        :param new_email: requested email value

        :return: None
        """

        if not isinstance(new_email, str):
            return

        if new_email == user.email:
            return

        existing = await self.repository.get_by_email(email=new_email)

        if existing is not None and existing.id != user.id:
            raise UserEmailAlreadyExists(email=new_email)

    def _enrich_password_change(
            self,
            user: User,
            schema: UpdateUserDTO,
            data: dict[str, object],
    ) -> None:
        """
        Apply password change validation and update payload enrichment.

        This method mutates the update payload only when password rotation is
        requested and credentials are verified.

        :param user: current user model
        :param schema: requested user updates
        :param data: update payload

        :return: None
        """
        new_password = schema.new_password

        if not new_password:
            return

        current_password = schema.current_password

        if not current_password:
            raise InvalidCredentials

        hashed_password = user.hashed_password

        if hashed_password is None:
            raise InvalidCredentials

        is_password_correct = self.auth_manager.verify_password_against_hash(
            plain_password=current_password,
            hashed_password=hashed_password,
        )

        if not is_password_correct:
            raise InvalidCredentials

        data["hashed_password"] = self.auth_manager.hash_password(password=new_password)
