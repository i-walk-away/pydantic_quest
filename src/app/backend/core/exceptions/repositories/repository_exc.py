from uuid import UUID


class RepositoryError(Exception):
    """
    Base repository exception class.
    """

class NotFoundError(RepositoryError):
    def __init__(
            self,
            entity_type: str,
            id: UUID
    ):
        self.entity_type = entity_type
        self.id = id

        super().__init__(f'{entity_type} with id {id} not found in the database.')



