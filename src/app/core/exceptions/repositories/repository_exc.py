from uuid import UUID

from fastapi import HTTPException


class RepositoryError(HTTPException):
    """
    Base repository exception class.
    """


class IDNotFoundError(RepositoryError):
    def __init__(
            self,
            entity_type_str: str,
            id: UUID
    ):
        """
        Initialize not found by id error.

        :param entity_type_str: entity type name
        :param id: entity id

        :return: None
        """
        self.status_code = 404

        super().__init__(
            status_code=self.status_code,
            detail=f'{entity_type_str} with id {id} not found in the database.'
        )


class NameNotFound(RepositoryError):
    def __init__(
            self,
            entity_type_str: str,
            name: str
    ):
        """
        Initialize not found by name error.

        :param entity_type_str:
        :param name:
        """
        self.status_code = 404

        super().__init__(
            status_code=self.status_code,
            detail=f'{entity_type_str} with name {name} not found in the database.'
        )


linter_testing = govnosral