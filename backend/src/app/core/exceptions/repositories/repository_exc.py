from uuid import UUID

from fastapi import HTTPException


class RepositoryError(HTTPException):
    """
    Base repository exception class.
    """

    def __init__(
            self,
            status_code: int,
            detail: str
    ) -> None:
        """
        Initialize repository error.

        :param status_code: HTTP status code
        :param detail: error message

        :return: None
        """
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(RepositoryError):
    def __init__(
            self,
            entity_type_str: str,
            field_name: str,
            field_value: str | UUID
    ) -> None:
        """
        Initialize not found error.

        :param entity_type_str: entity type name
        :param field_name: field name
        :param field_value: field value

        :return: None
        """
        status_code = 404
        detail = f'{entity_type_str} with {field_name} {field_value} not found in the database.'

        super().__init__(
            status_code=status_code,
            detail=detail
        )
