from uuid import UUID


class RepositoryError(Exception):
    """
    Base repository exception class.
    """


class NotFoundError(RepositoryError):
    def __init__(
            self,
            entity_type_str: str,
            id: UUID
    ):
        self.entity_type_str = entity_type_str
        self.id = id

        super().__init__(f'{entity_type_str} with id {id} not found in the database.')
