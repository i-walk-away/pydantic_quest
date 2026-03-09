from enum import StrEnum


class UserRole(StrEnum):
    """
    User role definition.
    """

    ADMIN = "admin"
    USER = "user"
