from uuid import UUID

from fastapi import HTTPException


class RepositoryError(HTTPException):
    """
    Base repository exception class.
    """


class NotFoundError(RepositoryError):
    def __init__(
            self,
            entity_type_str: str,
            id: UUID
    ):
        """
        Initialize not found error.

        :param entity_type_str: entity type name
        :param id: entity id

        :return: None
        """
        self.status_code = 404
        self.entity_type_str = entity_type_str
        self.id = id

        super().__init__(
            status_code=self.status_code,
            detail=f'{entity_type_str} with id {id} not found in the database.'
        )
