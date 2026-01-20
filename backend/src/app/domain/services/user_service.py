from uuid import UUID

from src.app.domain.models.db.user import User
from src.app.domain.models.dto.user import CreateUserDTO, UserDTO
from src.app.domain.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        """
        Initialize user service.

        :param user_repository: user repository

        :return: None
        """
        self.repository = user_repository

    async def get_by_id(self, id: UUID) -> UserDTO:
        """
        Get user by id.

        :param id: user id

        :return: user dto
        """
        result = await self.repository.get(id=id)
        return result.to_dto()

    async def get_by_username(self, username: str) -> UserDTO | None:
        """
        Gets user by username from the database.

        :param username: user's username
        :return: UserDTO representing a user.
        """
        user = await self.repository.get_by_username(username=username)

        if not user:
            return None

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
        data = schema.model_dump()

        user = User(
            **data
        )

        await self.repository.add(user)
        await self.repository.session.commit()
        await self.repository.session.refresh(user)

        return user.to_dto()

    async def delete(self, id: UUID) -> bool:
        """
        Delete user from the database.

        :param id: user id

        :return: ``True`` if user was deleted
        """
        deleted = await self.repository.delete(id=id)
        await self.repository.session.commit()

        return deleted
