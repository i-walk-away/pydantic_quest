from uuid import UUID

from src.app.core.exceptions.auth_exc import InvalidCredentials
from src.app.core.exceptions.base_exc import NotFoundError
from src.app.core.exceptions.user_exc import (
    UserAlreadyExists,
    UserEmailAlreadyExists,
    UserPasswordChangeInvalid,
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
        user = await self.repository.get(id=id)

        if not user:
            raise NotFoundError(
                entity_type_str='User',
                field_name='id',
                field_value=id,
            )

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
        user = await self.repository.get_by_username(username=schema.username)

        if user:
            raise UserAlreadyExists(username=user.username)

        hashed_password = self.auth_manager.hash_password(password=schema.plain_password)
        data = schema.model_dump()

        user = User(
            **data,
            hashed_password=hashed_password,
        )

        await self.repository.add(user)
        await self.repository.session.commit()
        await self.repository.session.refresh(user)

        return user.to_dto()

    async def delete(self, id: UUID) -> bool:
        """
        Delete user from the database.

        :param id: user id

        :return: True if user was deleted
        """
        user = self.repository.get(id=id)

        if not user:
            raise NotFoundError(
                entity_type_str='User',
                field_name='id',
                field_value=id,
            )

        deleted = await self.repository.delete(id=id)
        await self.repository.session.commit()

        return deleted

    async def update_me(self, id: UUID, schema: UpdateUserDTO) -> UserDTO:
        """
        Update current user data.

        :param id: user id
        :param schema: update data

        :return: updated user dto
        """
        user = await self.repository.get(id=id)
        if not user:
            raise NotFoundError(
                entity_type_str='User',
                field_name='id',
                field_value=id,
            )

        data = schema.model_dump(exclude_unset=True, exclude_none=True)

        username = data.get("username")
        if username and username != user.username:
            existing = await self.repository.get_by_username(username=username)
            if existing and existing.id != user.id:
                raise UserAlreadyExists(username=username)

        email = data.get("email")
        if email and email != user.email:
            existing = await self.repository.get_by_email(email=email)
            if existing and existing.id != user.id:
                raise UserEmailAlreadyExists(email=email)

        new_password = schema.new_password
        current_password = schema.current_password
        if new_password:
            if not current_password:
                raise UserPasswordChangeInvalid(detail="Current password is required.")

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

        data.pop("current_password", None)
        data.pop("new_password", None)

        updated = await self.repository.update(id=id, data=data)
        await self.repository.session.commit()
        await self.repository.session.refresh(updated)

        return updated.to_dto()
